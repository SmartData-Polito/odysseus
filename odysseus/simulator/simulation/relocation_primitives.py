import datetime
import json
import os

import numpy as np
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


class RelocationPrimitives:

    def __init__(self, env, sim):

        self.env = env

        self.start = sim.start

        self.sim_input = sim.sim_input

        self.vehicles_soc_dict = sim.vehicles_soc_dict

        self.vehicles_list = sim.vehicles_list

        self.available_vehicles_dict = sim.available_vehicles_dict

        self.zone_dict = sim.zone_dict

        self.vehicles_zones = sim.vehicles_zones

        self.relocation_workers_resource = simpy.Resource(
            self.env,
            capacity=self.sim_input.supply_model_config["n_relocation_workers"]
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
        self.sim_zones_relocations = []

        self.n_vehicles_tot = 0

        self.n_scooters_relocating = 0

        self.scheduled_relocations = []
        self.starting_zone_ids = []
        self.n_picked_vehicles_list = []
        self.ending_zone_ids = []
        self.n_dropped_vehicles_list = []

        self.sim_metrics = sim.sim_metrics

        self.relocation_workers = []

        for i in range(len(self.sim_input.supply_model.initial_relocation_workers_positions)):
            worker_id = i
            initial_position = self.sim_input.supply_model.initial_relocation_workers_positions[i]
            self.relocation_workers.append(Worker(env, worker_id, initial_position))

        if "window_width" in dict(self.sim_input.supply_model_config["relocation_technique"]):
            self.window_width = dict(self.sim_input.supply_model_config["relocation_technique"])["window_width"]
        else:
            self.window_width = 1

        if self.sim_input.supply_model_config["relocation_strategy"] == "predictive":

            from odysseus.simulator.simulation_input.prediction_model import PredictionModel

            prediction_model_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "simulator",
                "simulation_input",
                "prediction_model",
                self.sim_input.supply_model_config["city"]
            )

            with open(os.path.join(prediction_model_dir, "params.json"), "r") as f:
                prediction_model_configs = json.load(f)

            self.city_shape = self.sim_input.grid_matrix.shape
            mask = self.sim_input.grid_matrix.apply(lambda zone_id_column: zone_id_column.apply(
                lambda zone_id: int(zone_id in self.sim_input.valid_zones))).to_numpy()
            mask = np.repeat(mask[:, :, np.newaxis], 2, axis=2)

            prediction_model_path = os.path.join(prediction_model_dir,
                                                 prediction_model_configs["time_horizon_two"]["weights"])

            self.prediction_model_time_horizon_two = PredictionModel(prediction_model_configs["time_horizon_two"],
                                                                     self.city_shape,
                                                                     8, mask=mask, path=prediction_model_path)

            if self.window_width == 2:
                prediction_model_path = os.path.join(prediction_model_dir,
                                                     prediction_model_configs["time_horizon_three"]["weights"])

                self.prediction_model_time_horizon_three = PredictionModel(
                    prediction_model_configs["time_horizon_three"], self.city_shape,
                    8, mask=mask, path=prediction_model_path)

    def relocate_single_zone(self, relocation_record, move_vehicles=False, worker=None):

        with self.relocation_workers_resource.request() as relocation_worker_request:
            yield relocation_worker_request

            if worker:
                worker.start_working()

            self.n_scooters_relocating += len(relocation_record["vehicle_ids"])
            yield self.env.timeout(relocation_record["duration"])
            self.n_scooters_relocating -= len(relocation_record["vehicle_ids"])

            if worker:
                worker.stop_working()
                worker.update_position(relocation_record["end_zone_ids"][0])

        if move_vehicles:

            self.pick_up_scooter(
                relocation_record["start_zone_ids"][0],
                relocation_record["start_time"],
                move_vehicles=True,
                vehicle_ids=relocation_record["vehicle_ids"]
            )
            self.drop_off_scooter(
                relocation_record["end_zone_ids"][0],
                relocation_record["end_time"],
                move_vehicles=True,
                vehicle_ids=relocation_record["vehicle_ids"]
            )

        else:

            self.pick_up_scooter(
                relocation_record["start_zone_ids"][0],
                relocation_record["start_time"]
            )

            self.drop_off_scooter(
                relocation_record["end_zone_ids"][0],
                relocation_record["end_time"]
            )

        self.update_relocation_stats(relocation_record)

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
                    self.sim_input.grid,
                    step_start,
                    step_end,
                    self.sim_input.grid_crs
                )
                # distance = self.sim_input.distance_matrix.loc[step_start, step_end]

                total_distance += distance
                self.sim_metrics.update_metrics("avg_relocation_step_distance", distance)

                duration = distance / 1000 / self.sim_input.supply_model_config["avg_relocation_speed"] * 3600
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

                self.sim_zones_relocations.append({
                    "timestamp": current_time,
                    "zone_start": step_start,
                    "zone_end": step_end,
                    "operation_type": "pickup",
                    "n_vehicles": actual_n_picked_vehicles

                })

                self.n_scooters_relocating += actual_n_picked_vehicles

            # Prosecute navigation through distribution path
            for j in range(1, len(distribution_path)):
                # Step definition
                step_start = distribution_path[j - 1]
                step_end = distribution_path[j]

                distance = get_od_distance(
                    self.sim_input.grid,
                    step_start,
                    step_end,
                    self.sim_input.grid_crs
                )
                # distance = self.sim_input.distance_matrix.loc[step_start, step_end]
                total_distance += distance
                self.sim_metrics.update_metrics("avg_relocation_step_distance", distance)

                duration = distance / 1000 / self.sim_input.supply_model_config["avg_relocation_speed"] * 3600
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

                self.sim_zones_relocations.append({
                    "timestamp": current_time,
                    "zone_start": step_start,
                    "zone_end": step_end,
                    "operation_type": "dropoff",
                    "n_vehicles": actual_n_dropped_vehicles

                })

                self.n_scooters_relocating -= actual_n_dropped_vehicles

            worker.stop_working()

        # Save cumulative relocation stats
        scooter_relocation = init_scooter_relocation(
            relocated_vehicles,
            current_time,
            collection_path[1:],
            distribution_path[1:],
            total_distance,
            total_duration,
            worker_id=worker.id
        )

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
        if "save_history" in self.sim_input.sim_general_config:
            if self.sim_input.sim_general_config["save_history"]:
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

        if "save_history" in self.sim_input.sim_general_config:
            if self.sim_input.sim_general_config["save_history"]:
                self.sim_scooter_relocations += [scooter_relocation]

        self.n_scooter_relocations += 1
        self.tot_scooter_relocations_distance += scooter_relocation["distance"]
        self.tot_scooter_relocations_duration += scooter_relocation["duration"]
        self.n_vehicles_tot += scooter_relocation["n_vehicles"]

        self.sim_metrics.update_metrics("min_vehicles_relocated", scooter_relocation["n_vehicles"])
        self.sim_metrics.update_metrics("max_vehicles_relocated", scooter_relocation["n_vehicles"])
        self.sim_metrics.update_metrics("tot_vehicles_moved", scooter_relocation["n_vehicles"])

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
