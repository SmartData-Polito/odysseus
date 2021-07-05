import simpy
import datetime

from odysseus.utils.vehicle_utils import *
from odysseus.utils.geospatial_utils import get_od_distance


def init_relocate(charge_dict, vehicles_soc_dict, vehicle):
	relocate = {}
	relocate["plate"] = vehicle
	relocate["start_time"] = charge_dict["end_time"]
	relocate["date"] = charge_dict["start_time"].date()
	relocate["hour"] = charge_dict["start_time"].hour
	relocate["day_hour"] = charge_dict["start_time"].replace(minute=0, second=0, microsecond=0)
	relocate["start_soc"] = vehicles_soc_dict[vehicle]
	relocate["end_soc"] = vehicles_soc_dict[vehicle]
	relocate["soc_delta"] = relocate["end_soc"] - relocate["start_soc"]
	relocate["soc_delta_kwh"] = vehicle.tanktowheel_energy_from_perc(relocate["soc_delta"])
	return relocate


class RelocationPrimitives:

	def __init__(self, env, sim):

		self.env = env

		self.simInput = sim.simInput

		self.vehicles_soc_dict = sim.vehicles_soc_dict

		self.vehicles_list = sim.vehicles_list

		self.relocation_stations_dict = self.simInput.valid_zones

		self.zone_dict = sim.zone_dict

		self.workers = simpy.Resource(
			self.env,
			capacity=self.simInput.supply_model_conf["n_relocate_workers"]
		)

		# if self.simInput.sim_scenario_conf["hub"]:
		# 	self.charging_hub = simpy.Resource(
		# 		self.env,
		# 		capacity=self.simInput.hub_n_charging_poles
		# 	)

		# if self.simInput.sim_scenario_conf["distributed_cps"]:
		# 	self.n_charging_poles_by_zone = self.simInput.n_charging_poles_by_zone
		# 	self.charging_poles_dict = {}
		# 	for zone, n in self.n_charging_poles_by_zone.items():
		# 		if n > 0:
		# 			self.charging_poles_dict[zone] = simpy.Resource(
		# 				self.env,
		# 				capacity=n
		# 			)

		self.sim_relocates = []
		self.sim_unfeasible_relocate_chargings = []

		self.n_vehicles_relocating_system = 0
		# self.n_vehicles_charging_users = 0
		self.dead_vehicles = set()
		self.n_dead_vehicles = 0

		self.list_system_relocating_chargings = []

	# self.list_users_charging_bookings = []

	def relocate_vehicle(
			self,
			relocate_dict
	):

		relocate = relocate_dict["relocate"]
		resource = relocate_dict["resource"]
		vehicle_id = relocate_dict["vehicle"]
		operator = relocate_dict["operator"]
		zone_id = relocate_dict["zone_id"]
		# timeout_outward = relocate_dict["timeout_outward"]
		timeout_return = relocate_dict["timeout_return"]
		cr_soc_delta = relocate_dict["cr_soc_delta"]

		# def check_queuing():
		# 	if self.simInput.sim_scenario_conf["queuing"]:
		# 		return True
		# 	else:
		# 		if resource.count < resource.capacity:
		# 			return True
		# 		else:
		# 			return False

		relocate["operator"] = operator
		relocate["zone_id"] = zone_id
		# relocate["timeout_outward"] = timeout_outward
		relocate["timeout_return"] = timeout_return
		relocate["cr_soc_delta"] = cr_soc_delta
		relocate["cr_soc_delta_kwh"] = soc_to_kwh(cr_soc_delta)

		with self.workers.request() as worker_request:
			yield worker_request
			yield self.env.timeout(relocate["timeout_return"])
			# relocate["end"] = relocate["start"] - relocate["cr_soc_delta"]
			self.vehicles_soc_dict[vehicle_id] = relocate["end_soc"]
			relocate["end_soc"] -= relocate["cr_soc_delta"]

		# with resource.request() as charging_request:
		# 	yield charging_request
		# 	# self.n_vehicles_charging_system += 1
		# 	# yield self.env.timeout(charge["duration"])

		self.n_vehicles_relocating_system += 1
		self.zone_dict[relocate["zone_id"]].add_vehicle(
			relocate["start_time"]
		)
		# yield self.env.process(
		# 	self.relocation_stations_dict[zone_id].charge(
		# 		self.vehicles_list[vehicle_id],
		# 		charge["start_time"],
		# 		charge["cr_soc_delta"],
		# 		charge["duration"]
		# 	)
		# )

		self.n_vehicles_relocating_system -= 1
		relocate["end_time"] = relocate["start_time"] + datetime.timedelta(seconds=relocate["duration"])
		self.sim_relocates += [relocate]

	def check_system_relocate(self, charge_dict, vehicle):
		# have enough battery to relocate
		if self.vehicles_soc_dict[vehicle] > self.simInput.supply_model_conf["alpha"]:
			relocate = init_relocate(
				charge_dict,
				self.vehicles_soc_dict,
				vehicle
				# self.simInput.sim_scenario_conf["beta"]
			)
			return True, relocate
		else:
			return False, None

	# def check_user_relocate(self, charging_request, vehicle):
	#
	# 	if charging_request["destination_id"] in self.relocation_stations_dict:
	# 		if charging_request["end_soc"] < self.simInput.sim_scenario_conf["beta"]:
	# 			if np.random.binomial(1, self.simInput.sim_scenario_conf["willingness"]):
	# 				charge = init_relocate(
	# 					charge_dict,
	# 					self.vehicles_soc_dict,
	# 					vehicle,
	# 					self.simInput.sim_scenario_conf["beta"]
	# 				)
	# 				return True, charge
	# 			else:
	# 				return False, None
	# 		else:
	# 			return False, None
	# 	else:
	# 		return False, None
	def get_timeout(self, origin_id, destination_id):
		distance = get_od_distance(
			self.simInput.grid,
			origin_id,
			destination_id
		)
		if distance == 0:
			distance = self.simInput.demand_model_config["bin_side_length"]
		return distance / 1000 / self.simInput.avg_speed_kmh_mean * 3600

	def get_cr_soc_delta(self, origin_id, destination_id):
		distance = get_od_distance(
			self.simInput.grid,
			origin_id,
			destination_id
		)
		if distance == 0:
			distance = self.simInput.demand_model_config["bin_side_length"]
		return get_soc_delta(distance / 1000)
