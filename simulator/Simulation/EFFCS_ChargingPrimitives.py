import datetime

import numpy as np

from utils.car_utils import soc_to_kwh
from utils.car_utils import get_soc_delta


def get_charging_time (soc_delta,
					   battery_capacity = 3.5,
					   charging_efficiency = 0.92,
					   charger_rated_power = 3.7):

	return (soc_delta * 60 * battery_capacity) / (charging_efficiency * charger_rated_power * 100)


def get_charging_soc (duration,
					battery_capacity = 3.5,
					charging_efficiency = 0.92,
					charger_rated_power = 3.7):

	return (charging_efficiency * charger_rated_power * 100 * duration) / (60 * battery_capacity)


def init_charge (booking_request, cars_soc_dict, car, beta):

	charge = {}
	charge["plate"] = car
	charge["start_time"] = \
		booking_request["end_time"]
	charge["date"] = charge["start_time"].date()
	charge["hour"] = charge["start_time"].hour
	charge["day_hour"] = \
		charge["start_time"].replace(minute=0, second=0, microsecond=0)
	charge["start_soc"] = cars_soc_dict[car]
	charge["end_soc"] = beta

	return charge

def init_charge_end (charge, beta):
	charge["soc_delta"] = charge["end_soc"] - charge["start_soc"]
	charge["soc_delta_kwh"] = soc_to_kwh(charge["soc_delta"])
	charge["duration"] = \
		(get_charging_time(beta - charge["start_soc"]))
	return charge

class EFFCS_ChargingPrimitives ():

	def charge_car (self,
					charge,
					resource,
					car,
					operator,
					zone_id,
					timeout_outward = 0,
					timeout_return = 0,
					cr_soc_delta = 0
					):

		charge["operator"] = operator
		charge["zone_id"] = zone_id
		charge["timeout_outward"] = timeout_outward
		charge["timeout_return"] = timeout_return
		charge["cr_soc_delta"] = cr_soc_delta
		charge["cr_soc_delta_kwh"] = soc_to_kwh(cr_soc_delta)

		def check_queuing ():
			if self.simInput.sim_scenario_conf["queuing"]:
				return True
			else:
				if resource.count < resource.capacity:
					return True
				else:
					return False

		if operator == "system":
			if check_queuing():
				yield self.env.timeout(charge["timeout_outward"])
				charge["start_soc"] -= charge["cr_soc_delta"]
				charge = init_charge_end\
					(charge, self.simInput.sim_scenario_conf["beta"])
				if self.simInput.sim_scenario_conf["battery_swap"]:
					charge["duration"] = 0
				self.sim_charges += [charge]
				with resource.request() as charging_request:
					yield charging_request
					self.n_cars_charging_system += 1
					yield self.env.timeout(charge["duration"])
				self.n_cars_charging_system -= 1
				yield self.env.timeout(charge["timeout_return"])
				self.cars_soc_dict[car] = charge["end_soc"]
				charge["start_soc"] -= charge["cr_soc_delta"]
				charge["end_time"] = charge["start_time"] + \
					datetime.timedelta(seconds = charge["duration"] * 60 + 1)

		elif operator == "users":
			if resource.count < resource.capacity: # users never queue
				charge = init_charge_end\
					(charge, self.simInput.sim_scenario_conf["beta"])
				self.sim_charges += [charge]
				with resource.request() as charging_request:
					yield charging_request
					self.n_cars_charging_users += 1
					yield self.env.timeout(charge["duration"] * 60)
				self.cars_soc_dict[car] = charge["end_soc"]
				self.n_cars_charging_users -= 1
				charge["end_time"] = charge["start_time"] + \
					datetime.timedelta(seconds = charge["duration"] * 60)

	def check_system_charge (self, booking_request, car):

		if self.cars_soc_dict[car] < \
		self.simInput.sim_scenario_conf["alpha"]:
			charge = init_charge\
				(booking_request,
				 self.cars_soc_dict,
				 car,
				 self.simInput.sim_scenario_conf["beta"])
			return True, charge
		else:
			return False, None

	def check_user_charge (self, booking_request, car):

		if booking_request["end_soc"] < \
		self.simInput.sim_scenario_conf["beta"]:
			destination_id = booking_request["destination_id"]
			if destination_id in self.charging_poles_dict.keys():
				if np.random.binomial\
				(1, self.simInput.sim_scenario_conf["willingness"]):
					charge = init_charge\
						(booking_request,
						 self.cars_soc_dict,
						 car,
						 self.simInput.sim_scenario_conf["beta"])
					return True, charge
				else:
					return False, None
			else:
				return False, None
		else:
			return False, None

	def get_timeout (self, origin_id, destination_id):

		distance = self.simInput.od_distances.loc\
			[origin_id, destination_id] / 1000

		return distance / 15 * 3600

	def get_cr_soc_delta (self, origin_id, destination_id):

		distance = self.simInput.od_distances.loc\
			[origin_id, destination_id] / 1000

		return get_soc_delta(distance)
