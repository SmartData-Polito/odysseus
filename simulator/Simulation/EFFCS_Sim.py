import copy
import datetime
from functools import partial, wraps
import pytz

import simpy

from Simulation.EFFCS_ChargingStrategy import EFFCS_ChargingStrategy


class EFFCS_Sim ():

	def __init__ (
					self,
					simInput

				 ):

		self.start = datetime.datetime(
			simInput.sim_general_conf["year"],
			simInput.sim_general_conf["month_start"],
			1, tzinfo=pytz.UTC
		)
		self.end = datetime.datetime(
			simInput.sim_general_conf["year"],
			simInput.sim_general_conf["month_end"],
			1, tzinfo=pytz.UTC
		)
		self.total_seconds = (self.end - self.start).total_seconds()
		self.hours_spent = 0
		self.current_datetime = self.start
		self.current_hour = self.current_datetime.hour
		self.current_weekday = \
			self.current_datetime.weekday()
		if self.start.weekday() in [5, 6]:
			self.current_daytype = "weekend"
		else:
			self.current_daytype = "weekday"

		self.simInput = \
			simInput

		self.simInputCopy = \
			copy.deepcopy(simInput)

		self.available_cars_dict = \
			self.simInput.available_cars_dict

		self.neighbors_dict = \
			self.simInput.neighbors_dict

		if simInput.sim_scenario_conf["distributed_cps"]:
			self.n_charging_poles_by_zone = \
				self.simInput.n_charging_poles_by_zone

		self.cars_soc_dict = \
			self.simInput.cars_soc_dict

		self.cars_zones = \
			self.simInput.cars_zones

		self.env = simpy.Environment()

		self.events = []
		self.sim_booking_requests = []
		self.sim_booking_requests_deaths = []
		self.sim_unsatisfied_requests = []

		self.n_booking_requests = 0
		self.n_same_zone_trips = 0
		self.n_not_same_zone_trips = 0
		self.n_no_close_cars = 0
		self.n_deaths = 0

		self.n_booked_cars = 0

		self.list_n_cars_charging_system = []
		self.list_n_cars_charging_users = []
		self.list_n_cars_booked = []
		self.list_n_cars_available = []
		self.list_n_cars_dead = []

		self.chargingStrategy = \
			EFFCS_ChargingStrategy\
			(self.env,
			simInput)

	def schedule_booking (self, booking_request, car, zone_id):

		self.n_booked_cars += 1

		self.available_cars_dict\
			[zone_id].remove(car)
		del self.cars_zones[car]
		booking_request["start_soc"] = \
			self.cars_soc_dict[car]
		del self.cars_soc_dict[car]
		booking_request["plate"] = car

		yield self.env.timeout(booking_request["duration"] * 60)

		self.cars_soc_dict[car] = \
			booking_request["start_soc"] + booking_request["soc_delta"]
		booking_request["end_soc"] = \
			self.cars_soc_dict[car]
		self.cars_zones[car] = booking_request["destination_id"]

		self.n_booked_cars -= 1

		relocation_zone_id = \
			yield self.env.process\
				(self.chargingStrategy.check_charge\
				(booking_request, car))

		self.available_cars_dict\
			[relocation_zone_id].append(car)
		self.cars_zones[car] = relocation_zone_id

	def process_booking_request(self, booking_request):

		self.list_n_cars_booked += \
			[self.n_booked_cars]
		self.list_n_cars_charging_system += \
			[self.chargingStrategy.n_cars_charging_system]
		self.list_n_cars_charging_users += \
			[self.chargingStrategy.n_cars_charging_users]
		self.list_n_cars_dead += \
			[self.chargingStrategy.n_dead_cars]
		self.list_n_cars_available += \
			[self.simInput.n_cars - \
			 self.chargingStrategy.n_cars_charging_system - \
			 self.chargingStrategy.n_cars_charging_users - \
			 self.n_booked_cars]

		self.sim_booking_requests += [booking_request]
		self.n_booking_requests += 1

		available_car_flag = False
		found_car_flag = False
		available_car_flag_same_zone = False
		available_car_flag_not_same_zone = False

		def find_car (zone_id):
			available_cars_soc_dict = \
				{k:self.cars_soc_dict[k] for k in self.available_cars_dict[zone_id]}
			max_soc = max(available_cars_soc_dict.values())
			max_soc_car = \
				max(available_cars_soc_dict,
				key=available_cars_soc_dict.get)
			#print(booking_request)
			if self.cars_soc_dict[max_soc_car] > abs(booking_request["soc_delta"]):
				return True, max_soc_car, max_soc
			else:
				return False, max_soc_car, max_soc

		if len(self.available_cars_dict\
				   [booking_request["origin_id"]]):
			available_car_flag = True
			available_car_flag_same_zone = True
			found_car_flag, max_soc_car_origin, max_soc_origin = \
				find_car(booking_request["origin_id"])

		if found_car_flag:
			self.env.process\
				(self.schedule_booking\
				(booking_request, max_soc_car_origin, booking_request["origin_id"]))
			self.n_same_zone_trips += 1
		else:
			available_car_flag = False
			found_car_flag = False
			available_car_flag_same_zone = False
			available_car_flag_not_same_zone = False
			max_soc_car_neighbors = None
			max_soc_neighbors = -1
			max_neighbor = None
			for neighbor in self.neighbors_dict\
			[booking_request["origin_id"]].values():
				#print(neighbor)
				if neighbor in self.available_cars_dict:
					if len(self.available_cars_dict[neighbor]) and not found_car_flag:
						available_car_flag = True
						available_car_flag_not_same_zone = True
						found_car_flag, max_soc_car_neighbor, max_soc_neighbor = \
							find_car(neighbor)
						if max_soc_neighbors < max_soc_neighbor:
							max_neighbor = neighbor
							max_soc_car_neighbors = max_soc_car_neighbor
			if found_car_flag:
				self.env.process\
					(self.schedule_booking\
					(booking_request, max_soc_car_neighbors, max_neighbor))
				self.n_not_same_zone_trips += 1

		if not available_car_flag:
			self.n_no_close_cars += 1
			self.sim_unsatisfied_requests += [booking_request]

		if not found_car_flag and available_car_flag:
			self.n_deaths += 1
			death = copy.deepcopy(booking_request)
			death["hour"] = death["start_time"].hour
			#print(death["hour"])
			if available_car_flag_same_zone and available_car_flag_not_same_zone:
				if max_soc_origin > max_soc_neighbor:
					death["plate"] = max_soc_car_origin
					death["zone_id"] = booking_request["origin_id"]
				else:
					death["plate"] = max_soc_car_neighbor
					death["zone_id"] = max_neighbor
			elif available_car_flag_same_zone:
				death["plate"] = max_soc_car_origin
				death["zone_id"] = booking_request["origin_id"]
			elif available_car_flag_not_same_zone:
				death["plate"] = max_soc_car_neighbor
				death["zone_id"] = max_neighbor
			self.sim_booking_requests_deaths += [death]

	def trace(self, env, callback):

		def get_wrapper(env_step, callback):
			@wraps(env_step)
			def tracing_step():
				if len(env._queue):
					t, prio, eid, event = self.env._queue[0]
					callback(t, prio, eid, event)
				return env_step()
			return tracing_step

		self.env.step = get_wrapper(self.env.step, callback)

	def monitor(self, data, t, prio, eid, event):
		data.append((t, eid, type(event)))

	def run (self):
#        self.monitor = partial(self.monitor, self.events)
#        self.trace(self.env, self.monitor)
		self.env.process(self.mobility_requests_generator())
		self.env.run(until=self.total_seconds)
