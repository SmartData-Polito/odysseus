import simpy

from e3f2s.utils.geospatial_utils import get_od_distance


def init_vehicle_relocation(vehicle_id, start_time, start_zone_id, end_zone_id):
    #print("vehicle_id",vehicle_id)
    # soc_delta = VehicleRelocationPrimitives.get_cr_soc_delta(start_zone_id, end_zone_id, vehicle)
    # time_outward = VehicleRelocationPrimitives.get_timeout(start_zone_id, end_zone_id)
    vehicle_relocation = {
        "start_time": start_time,
	    # "time_outward": time_outward,
		"date": start_time.date(),
		"hour": start_time.hour,
		"day_hour": start_time.replace(minute=0, second=0, microsecond=0),
		# "plate": vehicle.plate,
		"vehicle_id": vehicle_id,
		"start_zone_id": start_zone_id,
		"end_zone_id": end_zone_id,
		"distance": None,
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

		self.workers = simpy.Resource(
			self.env,
			capacity=self.simInput.sim_scenario_conf["n_workers"]
		)

	def relocate_vehicle(self, vehicle_relocation, vehicle):

		#soc_delta = VehicleRelocationPrimitives.get_cr_soc_delta(vehicle_relocation["start_zone_id"],
																 #vehicle_relocation["end_zone_id"], vehicle)
		#time_outward = VehicleRelocationPrimitives.get_timeout(vehicle_relocation["start_zone_id"],
															  # vehicle_relocation["end_zone_id"])

		vehicle_relocation["distance"] = self.get_distance(
			vehicle_relocation["start_zone_id"],
			vehicle_relocation["end_zone_id"]
		)

		self.available_vehicles_dict[vehicle_relocation["start_zone_id"]].remove(
			vehicle_relocation["vehicle_id"]
		)

		self.zone_dict[vehicle_relocation["start_zone_id"]].remove_vehicle(
			vehicle_relocation["start_time"]
		)

		#yield self.env.timeout(time_outward)

		self.vehicles_zones[vehicle_relocation["vehicle_id"]] = vehicle_relocation["end_zone_id"]

		self.zone_dict[vehicle_relocation["end_zone_id"]].add_vehicle(
			vehicle_relocation["start_time"]
            #+ time_outward
		)

		self.available_vehicles_dict[vehicle_relocation["end_zone_id"]].append(
			vehicle_relocation["vehicle_id"]
		)

		#self.vehicles_soc_dict[vehicle_relocation["vehicle_id"]] = self.vehicles_soc_dict["vehicle_id"] - soc_delta
		self.sim_vehicle_relocations += [vehicle_relocation]

	def get_cr_soc_delta(self, origin_id, destination_id, vehicle):
		distance = get_od_distance(
			self.simInput.grid,
			origin_id,
			destination_id
		)
		if distance == 0:
			distance = self.simInput.sim_general_conf["bin_side_length"]
		return vehicle.consumption_to_percentage(vehicle.distance_to_consumption(distance / 1000))

	def get_distance(self, origin_id, destination_id):
		distance = get_od_distance(
			self.simInput.grid,
			origin_id,
			destination_id
		)
		if distance == 0:
			distance = self.simInput.sim_general_conf["bin_side_length"]
		return distance

	def get_timeout(self, origin_id, destination_id):
		distance = get_od_distance(
			self.simInput.grid,
			origin_id,
			destination_id
		)
		if distance == 0:
			distance = self.simInput.sim_general_conf["bin_side_length"]
		return distance / 1000 / self.simInput.avg_speed_kmh_mean * 3600
