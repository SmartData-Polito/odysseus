import simpy


from odysseus.utils.geospatial_utils import get_od_distance
#from odysseus.simulator.simulation.simulator import SharedMobilitySim


def init_vehicle_relocation(vehicle_ids, start_time, start_zone_id, end_zone_id, distance=None, duration=0):
	# print("vehicle_id",vehicle_id)
	# soc_delta = VehicleRelocationPrimitives.get_cr_soc_delta(start_zone_id, end_zone_id, vehicle)
	# time_outward = VehicleRelocationPrimitives.get_timeout(start_zone_id, end_zone_id)
	vehicle_relocation = {
		"start_time": start_time,
		"date": start_time.date(),
		"hour": start_time.hour,
		"day_hour": start_time.replace(minute=0, second=0, microsecond=0),
		"n_vehicles": len(vehicle_ids),
		# "plate": vehicle.plate,
		"vehicle_ids": vehicle_ids,
		"start_zone_id": start_zone_id,
		"end_zone_id": end_zone_id,
		"distance": distance,
		"duration":duration
		# "start_soc": sim.vehicles_soc_dict["vehicle_id"],
		# "end_soc": vehicle.soc.level - soc_delta,
		# "soc_delta": soc_delta
	}
	return vehicle_relocation


class VehicleRelocationPrimitives:

	def __init__(self, env, sim):

		self.env = env

		self.simInput = sim.simInput

		self.vehicles_soc_dict = sim.vehicles_soc_dict

		self.vehicles_list = sim.vehicles_list

		self.available_vehicles_dict = sim.available_vehicles_dict

		self.zone_dict = sim.zone_dict

		self.vehicles_zones = sim.vehicles_zones

		self.sim_vehicle_relocations = []

		self.relocation_workers = simpy.Resource(
			self.env,
			capacity=self.simInput.sim_scenario_conf["n_relocation_workers"]
		)

		self.n_vehicle_relocations = 0
		self.tot_vehicle_relocations_distance = 0
		self.tot_vehicle_relocations_duration = 0
		self.sim_vehicle_relocations = []

		self.n_vehicles_relocating = 0

		self.scheduled_vehicle_relocations = {}

	def relocate_vehicle(self, vehicle_relocation):

		# soc_delta = VehicleRelocationPrimitives.get_cr_soc_delta(vehicle_relocation["start_zone_id"],
		# vehicle_relocation["end_zone_id"], vehicle)
		# time_outward = VehicleRelocationPrimitives.get_timeout(vehicle_relocation["start_zone_id"],
		# vehicle_relocation["end_zone_id"])

		vehicle_relocation["distance"] = self.get_relocation_distance(vehicle_relocation)

		self.pick_up_vehicle(vehicle_relocation)

		# self.available_vehicles_dict[vehicle_relocation["start_zone_id"]].remove(
		# 	vehicle_relocation["vehicle_id"]
		# )

		# yield self.env.timeout(time_outward)

		with self.relocation_workers.request() as relocation_worker_request:
			yield relocation_worker_request
			self.n_vehicles_relocating += 1
			yield self.env.timeout(vehicle_relocation["duration"])
			self.n_vehicles_relocating -= 1

		self.drop_off_vehicle(vehicle_relocation)

		# self.vehicles_zones[vehicle_relocation["vehicle_id"]] = vehicle_relocation["end_zone_id"]
		#
		# self.available_vehicles_dict[vehicle_relocation["end_zone_id"]].append(
		# 	vehicle_relocation["vehicle_id"]
		# )

		# self.vehicles_soc_dict[vehicle_relocation["vehicle_id"]] = self.vehicles_soc_dict["vehicle_id"] - soc_delta
		self.sim_vehicle_relocations += [vehicle_relocation]

		self.n_vehicle_relocations += 1
		self.tot_vehicle_relocations_distance += vehicle_relocation["distance"]
		self.tot_vehicle_relocations_duration += vehicle_relocation["duration"]

	def get_cr_soc_delta(self, origin_id, destination_id, vehicle):
		distance = get_od_distance(
			self.simInput.grid,
			origin_id,
			destination_id
		)
		if distance == 0:
			distance = self.simInput.sim_general_conf["bin_side_length"]
		return vehicle.consumption_to_percentage(vehicle.distance_to_consumption(distance / 1000))

	def get_relocation_distance(self, vehicle_relocation):
		distance = get_od_distance(
			self.simInput.grid,
			vehicle_relocation["start_zone_id"],
			vehicle_relocation["end_zone_id"]
		)
		if distance == 0:
			distance = self.simInput.sim_general_conf["bin_side_length"]
		return distance

	def pick_up_vehicle(self, vehicle_relocation):
		self.zone_dict[vehicle_relocation["start_zone_id"]].remove_vehicle(
			vehicle_relocation["start_time"]
		)

	def drop_off_vehicle(self, vehicle_relocation):
		self.zone_dict[vehicle_relocation["end_zone_id"]].add_vehicle(
			vehicle_relocation["start_time"]
		)

	def get_timeout(self, origin_id, destination_id):
		distance = get_od_distance(
			self.simInput.grid,
			origin_id,
			destination_id
		)
		if distance == 0:
			distance = self.simInput.sim_general_conf["bin_side_length"]
		return distance / 1000 / self.simInput.avg_speed_kmh_mean * 3600
