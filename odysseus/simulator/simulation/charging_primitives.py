import simpy
import datetime
import numpy as np

from odysseus.utils.geospatial_utils import get_od_distance


def init_charge(booking_request, vehicle, beta):
	charge = {}
	charge["plate"] = vehicle.plate
	charge["start_time"] = booking_request["end_time"]
	charge["date"] = charge["start_time"].date()
	charge["hour"] = charge["start_time"].hour
	charge["day_hour"] = charge["start_time"].replace(minute=0, second=0, microsecond=0)
	charge["start_soc"] = vehicle.soc.level
	charge["end_soc"] = beta
	charge["soc_delta"] = charge["end_soc"] - charge["start_soc"]
	charge["soc_delta_kwh"] = vehicle.tanktowheel_energy_from_perc(charge["soc_delta"])
	return charge


class ChargingPrimitives:

	def __init__(self, env, sim):

		self.env = env
		self.sim_input = sim.sim_input
		self.vehicles_soc_dict = sim.vehicles_soc_dict
		self.vehicles_list = sim.vehicles_list
		self.charging_stations_dict = sim.charging_stations_dict
		self.zone_dict = sim.zone_dict

		if self.sim_input.supply_model_conf["battery_swap"] \
				and self.sim_input.supply_model_conf["scooter_relocation"]:
			self.scooterRelocationStrategy = sim.scooterRelocationStrategy

		self.workers = simpy.Resource(
			self.env,
			capacity=self.sim_input.supply_model_conf["n_workers"]
		)

		if self.sim_input.supply_model_conf["distributed_cps"]:
			self.n_charging_poles_by_zone = self.sim_input.supply_model.n_charging_poles_by_zone
			self.charging_poles_dict = {}
			for zone, n in self.n_charging_poles_by_zone.items():
				if n > 0:
					self.charging_poles_dict[zone] = simpy.Resource(
						self.env,
						capacity=n
					)

		self.n_charges = 0
		self.sim_charges = []
		self.sim_unfeasible_charge_bookings = []

		self.n_vehicles_charging_system = 0
		self.n_vehicles_charging_users = 0
		self.dead_vehicles = set()
		self.n_dead_vehicles = 0

		self.list_system_charging_bookings = []
		self.list_users_charging_bookings = []

		self.charging_return_distance = 0
		self.charging_outward_distance = 0

		self.sim_metrics = sim.sim_metrics

	def charge_vehicle(
			self,
			charge_dict
	):

		charge = charge_dict["charge"]
		resource = charge_dict["resource"]
		vehicle = charge_dict["vehicle"]
		operator = charge_dict["operator"]
		zone_id = charge_dict["zone_id"]
		timeout_outward = charge_dict["timeout_outward"]
		timeout_return = charge_dict["timeout_return"]
		cr_soc_delta = charge_dict["cr_soc_delta"]

		self.sim_metrics.update_metrics("cum_relo_ret_t", timeout_return)

		self.charging_outward_distance += charge_dict["charging_outward_distance"]

		def check_queuing():
			if self.sim_input.supply_model_conf["queuing"]:
				return True
			else:
				if resource.count < resource.capacity:
					return True
				else:
					return False

		charge["operator"] = operator
		charge["zone_id"] = zone_id
		charge["timeout_outward"] = timeout_outward
		charge["timeout_return"] = timeout_return
		charge["cr_soc_delta"] = cr_soc_delta
		charge["cr_soc_delta_kwh"] = vehicle.tanktowheel_energy_from_perc(cr_soc_delta)

		if self.sim_input.supply_model_conf["battery_swap"]:
			if operator == "system":
				if check_queuing():
					with self.workers.request() as worker_request:
						yield worker_request
						self.n_vehicles_charging_system += 1
						yield self.env.timeout(charge["timeout_outward"])
						#self.charging_outward_distance+=charge["charging_outward_distance"]
						yield self.env.timeout(charge["duration"])
						self.n_vehicles_charging_system -= 1
						yield self.env.timeout(charge["timeout_return"])
						#self.vehicles_soc_dict[vehicle_id] = charge["end_soc"]
						self.vehicles_list[vehicle.plate].charge(charge["soc_delta"])
			elif operator == "users":
				self.n_vehicles_charging_users += 1
				yield self.env.timeout(charge["duration"])
				#self.vehicles_soc_dict[vehicle_id] = charge["end_soc"]
				self.vehicles_list[vehicle.plate].charge(charge["soc_delta"])
				self.n_vehicles_charging_users -= 1

		else:
			if operator == "system":
				if check_queuing():
					with self.workers.request() as worker_request:
						yield worker_request
						yield self.env.timeout(charge["timeout_outward"])
						#self.charging_outward_distance += charge["charging_outward_distance"]
						charge["start_soc"] -= charge["cr_soc_delta"]
						yield self.env.timeout(charge["timeout_return"])
						#self.vehicles_soc_dict[vehicle_id] = charge["end_soc"]
						vehicle.charge(charge["soc_delta"])
						charge["end_soc"] -= charge["cr_soc_delta"]

					# with resource.request() as charging_request:
					# 	yield charging_request
					# 	# self.n_vehicles_charging_system += 1
					# 	# yield self.env.timeout(charge["duration"])

					self.n_vehicles_charging_system += 1
					self.zone_dict[charge["zone_id"]].add_vehicle(
						charge["start_time"] + datetime.timedelta(seconds=charge["duration"])
					)
					yield self.env.process(
						self.charging_stations_dict[zone_id].charge(
							vehicle,
							charge["start_time"],
							charge["cr_soc_delta"],
							charge["duration"]
						)
					)

					self.n_vehicles_charging_system -= 1

			elif operator == "users":
				if resource.count < resource.capacity:
					with resource.request() as charging_request:
						yield charging_request
						self.n_vehicles_charging_users += 1
						yield self.env.timeout(charge["duration"])
					#self.vehicles_soc_dict[vehicle_id] = charge["end_soc"]
					self.vehicles_list[vehicle.plate].charge(charge["soc_delta"])
					self.n_vehicles_charging_users -= 1

		charge["end_time"] = charge["start_time"] + datetime.timedelta(seconds=charge["duration"])

		if "save_history" in self.sim_input.sim_general_conf:
			if self.sim_input.sim_general_conf["save_history"]:
				self.sim_charges += [charge]
		self.n_charges += 1

	def check_system_charge(self, booking_request, vehicle, charging_strategy):
		if charging_strategy == "reactive":
			if vehicle.soc.level < self.sim_input.supply_model_conf["alpha"]:
				charge = init_charge(
					booking_request,
					vehicle,
					self.sim_input.supply_model_conf["beta"]
				)
				return True, charge
			else:
				return False, None
		else:
			print("No such charging strategy supported -> {}".format(charging_strategy))
			exit()

	def check_user_charge(self, booking_request, vehicle):

		if booking_request["destination_id"] in self.charging_stations_dict:
			if booking_request["end_soc"] < self.sim_input.supply_model_conf["beta"]:
				if np.random.binomial(1, self.sim_input.demand_model_conf["willingness"]):
					charge = init_charge(
						booking_request,
						self.vehicles_list[vehicle],
						self.sim_input.supply_model_conf["beta"]
					)
					return True, charge
				else:
					return False, None
			else:
				return False, None
		else:
			return False, None

	def get_timeout(self, origin_id, destination_id):
		distance = get_od_distance(
			self.sim_input.grid_centroids,
			origin_id,
			destination_id,
			self.sim_input.grid_crs
		)
		if distance == 0:
			distance = self.sim_input.supply_model.city_scenario.bin_side_length
		return distance / 1000 / self.sim_input.avg_speed_kmh_mean * 3600

	def get_cr_soc_delta(self, origin_id, destination_id, vehicle):
		distance = get_od_distance(
			self.sim_input.grid_centroids,
			origin_id,
			destination_id,
			self.sim_input.grid_crs
		)
		if distance == 0:
			distance = self.sim_input.supply_model.city_scenario.bin_side_length
		return vehicle.consumption_to_percentage(vehicle.distance_to_consumption(distance / 1000))

	def get_distance(self, origin_id, destination_id):
		distance = get_od_distance(
			self.sim_input.grid_centroids,
			origin_id,
			destination_id,
			self.sim_input.grid_crs
		)
		if distance == 0:
			distance = self.sim_input.supply_model.city_scenario.bin_side_length
		return distance
