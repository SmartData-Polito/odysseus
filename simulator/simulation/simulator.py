import copy
import datetime
from functools import partial, wraps
import pytz

import simpy

from simulator.simulation.charging_strategies import EFFCS_ChargingStrategy


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

		if simInput.sim_general_conf["month_end"] == 13:
			self.end = datetime.datetime(
				simInput.sim_general_conf["year"] + 1,
				1,
				1, tzinfo=pytz.UTC
			)
		else:
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

		self.simInput = simInput

		self.simInputCopy = copy.deepcopy(simInput)

		self.available_vehicles_dict = self.simInput.available_vehicles_dict

		self.neighbors_dict = self.simInput.neighbors_dict

		if simInput.sim_scenario_conf["distributed_cps"]:
			self.n_charging_poles_by_zone = self.simInput.n_charging_poles_by_zone

		self.vehicles_soc_dict = self.simInput.vehicles_soc_dict

		self.vehicles_zones = self.simInput.vehicles_zones

		self.env = simpy.Environment()

		self.events = []
		self.sim_booking_requests = []
		self.sim_booking_requests_deaths = []
		self.sim_unsatisfied_requests = []
		self.sim_no_close_vehicle_requests = []

		self.n_booking_requests = 0
		self.n_same_zone_trips = 0
		self.n_not_same_zone_trips = 0
		self.n_no_close_vehicles = 0
		self.n_deaths = 0

		self.n_booked_vehicles = 0

		self.list_n_vehicles_charging_system = []
		self.list_n_vehicles_charging_users = []
		self.list_n_vehicles_booked = []
		self.list_n_vehicles_available = []
		self.list_n_vehicles_dead = []
		self.vehicles_zones_history = []
		self.n_vehicles_per_zones_history = []

		self.chargingStrategy = EFFCS_ChargingStrategy(self.env, simInput)

	def schedule_booking (self, booking_request, vehicle, zone_id):

		#vehicle.booking(booking_request, zones[zone_id])

		self.available_vehicles_dict[zone_id].remove(vehicle)
		del self.vehicles_zones[vehicle]
		booking_request["start_soc"] = self.vehicles_soc_dict[vehicle]
		del self.vehicles_soc_dict[vehicle]

		self.n_booked_vehicles += 1

		booking_request["plate"] = vehicle

		yield self.env.timeout(booking_request["duration"])

		self.vehicles_soc_dict[vehicle] = booking_request["start_soc"] + booking_request["soc_delta"]
		booking_request["end_soc"] = self.vehicles_soc_dict[vehicle]
		self.vehicles_zones[vehicle] = booking_request["destination_id"]

		relocation_zone_id = yield self.env.process(
			self.chargingStrategy.check_charge(booking_request, vehicle)
		)

		self.available_vehicles_dict[relocation_zone_id].append(vehicle)
		self.vehicles_zones[vehicle] = relocation_zone_id

		self.n_booked_vehicles -= 1

	def process_booking_request(self, booking_request):

		self.list_n_vehicles_booked += [self.n_booked_vehicles]
		self.list_n_vehicles_charging_system += [self.chargingStrategy.n_vehicles_charging_system]
		self.list_n_vehicles_charging_users += [self.chargingStrategy.n_vehicles_charging_users]
		self.list_n_vehicles_dead += [self.chargingStrategy.n_dead_vehicles]
		n_vehicles_charging = self.chargingStrategy.n_vehicles_charging_system + self.chargingStrategy.n_vehicles_charging_users
		self.list_n_vehicles_available += [
			self.simInput.n_vehicles_sim - n_vehicles_charging - self.n_booked_vehicles
		]

		self.sim_booking_requests += [booking_request]
		self.n_booking_requests += 1

		available_vehicle_flag = False
		found_vehicle_flag = False
		available_vehicle_flag_same_zone = False
		available_vehicle_flag_not_same_zone = False

		def find_vehicle (zone_id):
			available_vehicles_soc_dict = {k: self.vehicles_soc_dict[k] for k in self.available_vehicles_dict[zone_id]}
			max_soc = max(available_vehicles_soc_dict.values())
			max_soc_vehicle = max(available_vehicles_soc_dict, key=available_vehicles_soc_dict.get)
			if self.vehicles_soc_dict[max_soc_vehicle] > abs(booking_request["soc_delta"]):
				return True, max_soc_vehicle, max_soc
			else:
				return False, max_soc_vehicle, max_soc

		if len(self.available_vehicles_dict[booking_request["origin_id"]]):
			available_vehicle_flag = True
			available_vehicle_flag_same_zone = True
			found_vehicle_flag, max_soc_vehicle_origin, max_soc_origin = \
				find_vehicle(booking_request["origin_id"])

		if found_vehicle_flag:
			self.env.process\
				(self.schedule_booking\
				(booking_request, max_soc_vehicle_origin, booking_request["origin_id"]))
			self.n_same_zone_trips += 1
		else:
			available_vehicle_flag = False
			found_vehicle_flag = False
			available_vehicle_flag_same_zone = False
			available_vehicle_flag_not_same_zone = False
			max_soc_vehicle_neighbors = None
			max_soc_neighbors = -1
			max_neighbor = None
			for neighbor in self.neighbors_dict[booking_request["origin_id"]].values():
				if neighbor in self.available_vehicles_dict:
					if len(self.available_vehicles_dict[neighbor]) and not found_vehicle_flag:
						available_vehicle_flag = True
						available_vehicle_flag_not_same_zone = True
						found_vehicle_flag, max_soc_vehicle_neighbor, max_soc_neighbor = \
							find_vehicle(neighbor)
						if max_soc_neighbors < max_soc_neighbor:
							max_neighbor = neighbor
							max_soc_vehicle_neighbors = max_soc_vehicle_neighbor
			if found_vehicle_flag:
				self.env.process\
					(self.schedule_booking\
					(booking_request, max_soc_vehicle_neighbors, max_neighbor))
				self.n_not_same_zone_trips += 1

		if not available_vehicle_flag:
			self.n_no_close_vehicles += 1
			self.sim_unsatisfied_requests += [booking_request]
			self.sim_no_close_vehicle_requests += [booking_request]

		if not found_vehicle_flag and available_vehicle_flag:
			self.n_deaths += 1
			death = copy.deepcopy(booking_request)
			death["hour"] = death["start_time"].hour
			if available_vehicle_flag_same_zone and available_vehicle_flag_not_same_zone:
				if max_soc_origin > max_soc_neighbor:
					death["plate"] = max_soc_vehicle_origin
					death["zone_id"] = booking_request["origin_id"]
				else:
					death["plate"] = max_soc_vehicle_neighbor
					death["zone_id"] = max_neighbor
			elif available_vehicle_flag_same_zone:
				death["plate"] = max_soc_vehicle_origin
				death["zone_id"] = booking_request["origin_id"]
			elif available_vehicle_flag_not_same_zone:
				death["plate"] = max_soc_vehicle_neighbor
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
