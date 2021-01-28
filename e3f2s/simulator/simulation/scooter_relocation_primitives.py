import simpy

from e3f2s.utils.geospatial_utils import get_od_distance


def init_scooter_relocation(vehicle_ids, start_time, start_zone_id, end_zone_id, distance=None, duration=0):

    scooter_relocation = {
        "start_time": start_time,
        "date": start_time.date(),
        "hour": start_time.hour,
        "day_hour": start_time.replace(minute=0, second=0, microsecond=0),
        "n_vehicles": len(vehicle_ids),
        "vehicle_ids": vehicle_ids,
        "start_zone_id": start_zone_id,
        "end_zone_id": end_zone_id,
        "distance": distance,
        "duration": duration
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

        self.relocation_workers = simpy.Resource(
            self.env,
            capacity=self.simInput.sim_scenario_conf["n_relocation_workers"]
        )

        self.n_scooter_relocations = 0
        self.tot_scooter_relocations_distance = 0
        self.tot_scooter_relocations_duration = 0
        self.sim_scooter_relocations = []
        self.n_vehicles_tot = 0

        self.n_scooters_relocating = 0

        self.scheduled_scooter_relocations = {}

    def relocate_scooter(self, scooter_relocation):

        scooter_relocation["distance"] = self.get_relocation_distance(scooter_relocation)

        self.pick_up_scooter(scooter_relocation)

        with self.relocation_workers.request() as relocation_worker_request:
            yield relocation_worker_request
            self.n_scooters_relocating += 1
            yield self.env.timeout(scooter_relocation["duration"])
            self.n_scooters_relocating -= 1

        self.drop_off_scooter(scooter_relocation)

        self.update_relocation_stats(scooter_relocation)

    def magically_relocate_scooter(self, scooter_relocation):
        scooter_relocation["distance"] = self.get_relocation_distance(scooter_relocation)
        self.pick_up_scooter(scooter_relocation)
        self.drop_off_scooter(scooter_relocation)
        if "save_history" in self.simInput.supply_model_conf:
            if self.simInput.supply_model_conf["save_history"]:
                self.sim_scooter_relocations += [scooter_relocation]
        self.n_scooter_relocations += 1
        self.tot_scooter_relocations_distance += scooter_relocation["distance"]
        self.n_vehicles_tot += scooter_relocation["n_vehicles"]

    def get_relocation_distance(self, scooter_relocation):
        return get_od_distance(
            self.simInput.grid,
            scooter_relocation["start_zone_id"],
            scooter_relocation["end_zone_id"]
        )

    def pick_up_scooter(self, scooter_relocation):
        self.zone_dict[scooter_relocation["start_zone_id"]].remove_vehicle(
            scooter_relocation["start_time"]
        )

    def drop_off_scooter(self, scooter_relocation):
        self.zone_dict[scooter_relocation["end_zone_id"]].add_vehicle(
            scooter_relocation["start_time"]
        )

    def update_relocation_stats(self, scooter_relocation):

        if "save_history" in self.simInput.supply_model_conf:
            if self.simInput.supply_model_conf["save_history"]:
                self.sim_scooter_relocations += [scooter_relocation]

        self.n_scooter_relocations += 1
        self.tot_scooter_relocations_distance += scooter_relocation["distance"]
        self.tot_scooter_relocations_duration += scooter_relocation["duration"]
        self.n_vehicles_tot += scooter_relocation["n_vehicles"]
