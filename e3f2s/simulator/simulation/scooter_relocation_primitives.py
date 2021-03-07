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

        self.start = sim.start

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

        self.current_hour_origin_count = {}
        self.current_hour_destination_count = {}
        self.current_hour_n_bookings = 0

        self.past_hours_origin_counts = []
        self.past_hours_destination_counts = []
        self.past_hours_n_bookings = []

        self.n_scooter_relocations = 0
        self.tot_scooter_relocations_distance = 0
        self.tot_scooter_relocations_duration = 0
        self.sim_scooter_relocations = []
        self.n_vehicles_tot = 0

        self.n_scooters_relocating = 0

        self.scheduled_scooter_relocations = {}
        self.starting_zone_ids = []
        self.ending_zone_ids = []

        self.sim_metrics = sim.sim_metrics

    def relocate_scooter(self, scooter_relocation, move_vehicles=False):

        scooter_relocation["distance"] = self.get_relocation_distance(scooter_relocation)

        self.pick_up_scooter(scooter_relocation, move_vehicles)

        with self.relocation_workers.request() as relocation_worker_request:
            yield relocation_worker_request
            self.n_scooters_relocating += 1
            yield self.env.timeout(scooter_relocation["duration"])
            self.n_scooters_relocating -= 1

        self.drop_off_scooter(scooter_relocation, move_vehicles)

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

    def pick_up_scooter(self, scooter_relocation, move_vehicles=False):
        self.zone_dict[scooter_relocation["start_zone_id"]].remove_vehicle(
            scooter_relocation["start_time"]
        )
        if move_vehicles:
            starting_zone_id = scooter_relocation["start_zone_id"]
            relocated_vehicles = scooter_relocation["vehicle_ids"]

            for vehicle in relocated_vehicles:
                if vehicle in self.available_vehicles_dict[starting_zone_id]:
                    self.available_vehicles_dict[starting_zone_id].remove(vehicle)
                if vehicle in self.vehicles_zones:
                    del self.vehicles_zones[vehicle]

    def drop_off_scooter(self, scooter_relocation, move_vehicles=False):
        self.zone_dict[scooter_relocation["end_zone_id"]].add_vehicle(
            scooter_relocation["start_time"]
        )
        if move_vehicles:
            ending_zone_id = scooter_relocation["end_zone_id"]
            relocated_vehicles = scooter_relocation["vehicle_ids"]

            for vehicle in relocated_vehicles:
                self.available_vehicles_dict[ending_zone_id].append(vehicle)
                self.vehicles_zones[vehicle] = ending_zone_id

    def update_relocation_stats(self, scooter_relocation):

        if "save_history" in self.simInput.supply_model_conf:
            if self.simInput.supply_model_conf["save_history"]:
                self.sim_scooter_relocations += [scooter_relocation]

        self.n_scooter_relocations += 1
        self.tot_scooter_relocations_distance += scooter_relocation["distance"]
        self.tot_scooter_relocations_duration += scooter_relocation["duration"]
        self.n_vehicles_tot += scooter_relocation["n_vehicles"]

        self.sim_metrics.update_metrics("min_vehicles_relocated", scooter_relocation["n_vehicles"])
        self.sim_metrics.update_metrics("max_vehicles_relocated", scooter_relocation["n_vehicles"])

    def update_current_hour_stats(self, booking_request):
        self.current_hour_n_bookings += 1

        if booking_request["origin_id"] in self.current_hour_origin_count:
            self.current_hour_origin_count[booking_request["origin_id"]] += 1
        else:
            self.current_hour_origin_count[booking_request["origin_id"]] = 1

        if booking_request["destination_id"] in self.current_hour_destination_count:
            self.current_hour_destination_count[booking_request["destination_id"]] += 1
        else:
            self.current_hour_destination_count[booking_request["destination_id"]] = 1

    def reset_current_hour_stats(self):
        self.current_hour_n_bookings = 0
        self.current_hour_origin_count = {}
        self.current_hour_destination_count = {}
