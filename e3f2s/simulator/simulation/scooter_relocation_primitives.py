from e3f2s.utils.geospatial_utils import get_od_distance


def init_scooter_relocation(vehicle_id, start_time, start_zone_id, end_zone_id):

    scooter_relocation = {
        "start_time": start_time,
        "date": start_time.date(),
        "hour": start_time.hour,
        "day_hour": start_time.replace(minute=0, second=0, microsecond=0),
        "vehicle_id": vehicle_id,
        "start_zone_id": start_zone_id,
        "end_zone_id": end_zone_id,
        "distance": None
    }
    return scooter_relocation


class ScooterRelocationPrimitives:

    def __init__(self, env, sim):

        self.env = env

        self.simInput = sim.simInput

        self.vehicles_soc_dict = sim.vehicles_soc_dict

        self.vehicles_list = sim.vehicles_list

        self.available_vehicles_dict = sim.available_vehicles_dict

        self.zone_dict = sim.zone_dict

        self.vehicles_zones = sim.vehicles_zones

        self.sim_scooter_relocations = []

    def relocate_scooter(self, scooter_relocation):

        scooter_relocation["distance"] = get_od_distance(
            self.simInput.grid,
            scooter_relocation["start_zone_id"],
            scooter_relocation["end_zone_id"]
        )

        self.vehicles_zones[scooter_relocation["vehicle_id"]] = scooter_relocation["end_zone_id"]

        self.available_vehicles_dict[scooter_relocation["start_zone_id"]].remove(
            scooter_relocation["vehicle_id"]
        )

        self.zone_dict[scooter_relocation["start_zone_id"]].remove_vehicle(
            scooter_relocation["start_time"]
        )
        self.zone_dict[scooter_relocation["end_zone_id"]].add_vehicle(
            scooter_relocation["start_time"]
        )

        self.available_vehicles_dict[scooter_relocation["end_zone_id"]].append(
            scooter_relocation["vehicle_id"]
        )

        self.sim_scooter_relocations += [scooter_relocation]
