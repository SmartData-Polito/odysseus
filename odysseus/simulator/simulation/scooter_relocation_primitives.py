import datetime

import simpy

from odysseus.simulator.simulation_data_structures.worker import Worker
from odysseus.utils.geospatial_utils import get_od_distance


def init_scooter_relocation(vehicle_ids, start_time, start_zone_ids, end_zone_ids, distance, duration, worker_id='ND'):

    scooter_relocation = {
        "start_time": start_time,
        "end_time": start_time + datetime.timedelta(seconds=duration),
        "date": start_time.date(),
        "hour": start_time.hour,
        "day_hour": start_time.replace(minute=0, second=0, microsecond=0),
        "n_vehicles": len(vehicle_ids),
        "vehicle_ids": vehicle_ids,
        "start_zone_ids": start_zone_ids,
        "end_zone_ids": end_zone_ids,
        "distance": distance,
        "duration": duration,
        "worker": worker_id
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

        self.relocation_workers_resource = simpy.Resource(
            self.env,
            capacity=self.simInput.sim_scenario_conf["n_relocation_workers"]
        )

        self.current_hour_origin_count = {}
        self.current_hour_destination_count = {}

        self.past_hours_origin_counts = []
        self.past_hours_destination_counts = []
        self.past_hours_n_bookings = []

        self.n_scooter_relocations = 0
        self.tot_scooter_relocations_distance = 0
        self.tot_scooter_relocations_duration = 0
        self.sim_scooter_relocations = []
        self.n_vehicles_tot = 0

        self.n_scooters_relocating = 0

        self.scheduled_scooter_relocations = []
        self.starting_zone_ids = []
        self.n_picked_vehicles_list = []
        self.ending_zone_ids = []
        self.n_dropped_vehicles_list = []

        self.sim_metrics = sim.sim_metrics

        self.relocation_workers = []

        for i in range(len(self.simInput.supply_model.initial_relocation_workers_positions)):
            worker_id = i
            initial_position = self.simInput.supply_model.initial_relocation_workers_positions[i]
            self.relocation_workers.append(Worker(env, worker_id, initial_position))

    def relocate_scooter_single_zone(self, scooter_relocation, move_vehicles=False, worker=None):

        with self.relocation_workers_resource.request() as relocation_worker_request:
            yield relocation_worker_request

            if worker:
                worker.start_working()

            self.n_scooters_relocating += len(scooter_relocation["vehicle_ids"])
            yield self.env.timeout(scooter_relocation["duration"])
            self.n_scooters_relocating -= len(scooter_relocation["vehicle_ids"])

            if worker:
                worker.stop_working()
                worker.update_position(scooter_relocation["end_zone_ids"][0])

        if move_vehicles:

            self.pick_up_scooter(
                scooter_relocation["start_zone_ids"][0],
                scooter_relocation["start_time"],
                move_vehicles=True,
                vehicle_ids=scooter_relocation["vehicle_ids"]
            )
            self.drop_off_scooter(
                scooter_relocation["end_zone_ids"][0],
                scooter_relocation["end_time"],
                move_vehicles=True,
                vehicle_ids=scooter_relocation["vehicle_ids"]
            )

        else:

            self.pick_up_scooter(
                scooter_relocation["start_zone_ids"][0],
                scooter_relocation["start_time"]
            )

            self.drop_off_scooter(
                scooter_relocation["end_zone_ids"][0],
                scooter_relocation["end_time"]
            )

        self.update_relocation_stats(scooter_relocation)

    def relocate_scooter_multiple_zones(self, scheduled_relocation, collection_path, distribution_path, worker):
        with self.relocation_workers_resource.request() as relocation_worker_request:
            yield relocation_worker_request

            worker.start_working()

            total_distance = 0
            total_duration = 0
            picked_vehicles = []
            relocated_vehicles = []

            # Navigate through collection path
            for j in range(1, len(collection_path)):
                # Step definition
                step_start = collection_path[j - 1]
                step_end = collection_path[j]

                distance = get_od_distance(
                    self.simInput.grid,
                    step_start,
                    step_end
                )
                total_distance += distance
                self.sim_metrics.update_metrics("avg_relocation_step_distance", distance)

                duration = distance / 1000 / self.simInput.supply_model_conf["avg_relocation_speed"] * 3600
                total_duration += duration

                # Simulate step navigation time
                yield self.env.timeout(duration)
                worker.update_position(step_end)

                # Pick up programmed scooters where available
                current_time = self.start + datetime.timedelta(seconds=self.env.now)

                actual_n_picked_vehicles = min(
                    scheduled_relocation["pick_up"][step_end],
                    len(self.available_vehicles_dict[step_end])
                )

                for k in range(actual_n_picked_vehicles):
                    picked_vehicle = self.available_vehicles_dict[step_end].pop()
                    picked_vehicles.append(picked_vehicle)
                    self.pick_up_scooter(step_end, current_time)

                self.n_scooters_relocating += actual_n_picked_vehicles

            # Prosecute navigation through distribution path
            for j in range(1, len(distribution_path)):
                # Step definition
                step_start = distribution_path[j - 1]
                step_end = distribution_path[j]

                distance = get_od_distance(
                    self.simInput.grid,
                    step_start,
                    step_end
                )
                total_distance += distance
                self.sim_metrics.update_metrics("avg_relocation_step_distance", distance)

                duration = distance / 1000 / self.simInput.supply_model_conf["avg_relocation_speed"] * 3600
                total_duration += duration

                # Simulate step navigation time
                yield self.env.timeout(duration)
                worker.update_position(step_end)

                # Drop off programmed scooters while available
                current_time = self.start + datetime.timedelta(seconds=self.env.now)

                actual_n_dropped_vehicles = min(
                    scheduled_relocation["drop_off"][step_end],
                    len(picked_vehicles)
                )

                for k in range(actual_n_dropped_vehicles):
                    dropped_vehicle = picked_vehicles.pop()
                    relocated_vehicles.append(dropped_vehicle)
                    self.available_vehicles_dict[step_end].append(dropped_vehicle)
                    self.drop_off_scooter(step_end, current_time)

                self.n_scooters_relocating -= actual_n_dropped_vehicles

            worker.stop_working()

        # Save cumulative relocation stats
        scooter_relocation = init_scooter_relocation(relocated_vehicles, current_time,
                                                     collection_path[1:], distribution_path[1:],
                                                     total_distance, total_duration, worker_id=worker.id)

        self.update_relocation_stats(scooter_relocation)

    def magically_relocate_scooter(self, scooter_relocation):
        self.pick_up_scooter(
            scooter_relocation["start_zone_ids"][0],
            scooter_relocation["start_time"]
        )
        self.drop_off_scooter(
            scooter_relocation["end_zone_ids"][0],
            scooter_relocation["end_time"]
        )
        if "save_history" in self.simInput.supply_model_conf:
            if self.simInput.supply_model_conf["save_history"]:
                self.sim_scooter_relocations += [scooter_relocation]
        self.n_scooter_relocations += 1
        self.tot_scooter_relocations_distance += scooter_relocation["distance"]
        self.n_vehicles_tot += scooter_relocation["n_vehicles"]

    def pick_up_scooter(self, zone_id, time, move_vehicles=False, vehicle_ids=None):
        self.zone_dict[zone_id].remove_vehicle(time)
        if move_vehicles:
            starting_zone_id = zone_id
            relocated_vehicles = vehicle_ids

            for vehicle in relocated_vehicles:
                if vehicle in self.available_vehicles_dict[starting_zone_id]:
                    self.available_vehicles_dict[starting_zone_id].remove(vehicle)
                if vehicle in self.vehicles_zones:
                    del self.vehicles_zones[vehicle]

    def drop_off_scooter(self, zone_id, time, move_vehicles=False, vehicle_ids=None):
        self.zone_dict[zone_id].add_vehicle(time)
        if move_vehicles:
            ending_zone_id = zone_id
            relocated_vehicles = vehicle_ids

            for vehicle in relocated_vehicles:
                self.available_vehicles_dict[ending_zone_id].append(vehicle)
                self.vehicles_zones[vehicle] = ending_zone_id

    def update_relocation_stats(self, scooter_relocation):

        if "save_history" in self.simInput.demand_model_config:
            if self.simInput.demand_model_config["save_history"]:
                self.sim_scooter_relocations += [scooter_relocation]

        self.n_scooter_relocations += 1
        self.tot_scooter_relocations_distance += scooter_relocation["distance"]
        self.tot_scooter_relocations_duration += scooter_relocation["duration"]
        self.n_vehicles_tot += scooter_relocation["n_vehicles"]

        self.sim_metrics.update_metrics("min_vehicles_relocated", scooter_relocation["n_vehicles"])
        self.sim_metrics.update_metrics("max_vehicles_relocated", scooter_relocation["n_vehicles"])

    def update_current_hour_stats(self, booking_request):

        if booking_request["origin_id"] in self.current_hour_origin_count:
            self.current_hour_origin_count[booking_request["origin_id"]] += 1
        else:
            self.current_hour_origin_count[booking_request["origin_id"]] = 1

        if booking_request["destination_id"] in self.current_hour_destination_count:
            self.current_hour_destination_count[booking_request["destination_id"]] += 1
        else:
            self.current_hour_destination_count[booking_request["destination_id"]] = 1

    def reset_current_hour_stats(self):
        self.current_hour_origin_count = {}
        self.current_hour_destination_count = {}
