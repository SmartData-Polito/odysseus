import numpy as np
from e3f2s.simulator.simulation.scooter_relocation_primitives import *


class ScooterRelocationStrategy(ScooterRelocationPrimitives):

    def check_scooter_relocation(self, booking_request, vehicles=None):

        relocated = False
        relocated_vehicles = vehicles
        scooter_relocation = {}

        if self.simInput.supply_model_conf["battery_swap"]:

            if self.simInput.supply_model_conf["scooter_relocation_strategy"] == "magic_relocation":

                booking_request_zone_column = int(np.floor(
                    booking_request["origin_id"] / self.simInput.grid_matrix.shape[0]
                ))
                booking_request_zone_row = int(
                    booking_request["origin_id"] - booking_request_zone_column * self.simInput.grid_matrix.shape[0]
                )

                found_vehicle_flag = False
                r = 2  # excludes origin zone and its neighbors

                while not found_vehicle_flag and r < max(self.simInput.grid_matrix.shape):

                    zones_ring = []
                    available_vehicles_soc_dict = {}

                    i = booking_request_zone_row - r
                    j = booking_request_zone_column - r
                    if i >= 0 and j >= 0:
                        while j < booking_request_zone_column + r and j < self.simInput.grid_matrix.shape[1]:
                            zones_ring.append(self.simInput.grid_matrix.iloc[i, j])
                            j += 1

                    i = booking_request_zone_row - r
                    j = booking_request_zone_column + r
                    if i >= 0 and j < self.simInput.grid_matrix.shape[1]:
                        while i < booking_request_zone_row + r and i < self.simInput.grid_matrix.shape[0]:
                            zones_ring.append(self.simInput.grid_matrix.iloc[i, j])
                            i += 1

                    i = booking_request_zone_row + r
                    j = booking_request_zone_column + r
                    if i < self.simInput.grid_matrix.shape[0] and j < self.simInput.grid_matrix.shape[1]:
                        while j > booking_request_zone_column - r and j > 0:
                            zones_ring.append(self.simInput.grid_matrix.iloc[i, j])
                            j -= 1

                    i = booking_request_zone_row + r
                    j = booking_request_zone_column - r
                    if i < self.simInput.grid_matrix.shape[0] and j >= 0:
                        while i > booking_request_zone_row - r and i > 0:
                            zones_ring.append(self.simInput.grid_matrix.iloc[i, j])
                            i -= 1

                    for zone_id in zones_ring:
                        if zone_id in self.available_vehicles_dict and len(self.available_vehicles_dict[zone_id]):
                            for available_vehicle in self.available_vehicles_dict[zone_id]:
                                available_vehicles_soc_dict[available_vehicle] = self.vehicles_list[available_vehicle].soc.level

                    if len(available_vehicles_soc_dict):
                        max_soc_vehicle = max(available_vehicles_soc_dict, key=available_vehicles_soc_dict.get)
                        max_soc_vehicle_zone = self.vehicles_zones[max_soc_vehicle]

                        if self.vehicles_list[max_soc_vehicle].soc.level > abs(
                            self.vehicles_list[max_soc_vehicle].consumption_to_percentage(
                                self.vehicles_list[max_soc_vehicle].distance_to_consumption(
                                    booking_request["driving_distance"] / 1000
                                )
                            )
                        ):
                            found_vehicle_flag = True

                    r += 1

                if found_vehicle_flag:

                    relocated = True
                    relocation_zone_id = booking_request["origin_id"]
                    relocated_vehicles = [max_soc_vehicle]

                    scooter_relocation = init_scooter_relocation(
                        relocated_vehicles,
                        booking_request["start_time"],
                        max_soc_vehicle_zone,
                        relocation_zone_id)

            else:

                relocation_zone_id = None

                if "scooter_relocation_scheduling" in self.simInput.sim_scenario_conf.keys() \
                        and self.simInput.sim_scenario_conf["scooter_relocation_scheduling"]:

                    if booking_request["destination_id"] in self.scheduled_scooter_relocations \
                            and len(self.scheduled_scooter_relocations[booking_request["destination_id"]]):

                        scheduled_relocation = self.scheduled_scooter_relocations[booking_request["destination_id"]].popitem()

                        relocation_zone_id = scheduled_relocation[0]
                        n_relocated_vehicles = scheduled_relocation[1]

                        for i in range(1, min(n_relocated_vehicles, len(self.available_vehicles_dict[booking_request["destination_id"]]))):  # first vehicle is charged vehicle
                            relocated_vehicle = self.available_vehicles_dict[booking_request["destination_id"]].pop()
                            relocated_vehicles.append(relocated_vehicle)

                else:
                    relocation_zone_id = self.choose_ending_zone(
                        daytype=booking_request["daytype"],
                        hour=booking_request["hour"]
                    )[0]

                if relocation_zone_id and relocation_zone_id != booking_request["destination_id"]:

                    relocated = True

                    distance = get_od_distance(
                        self.simInput.grid,
                        booking_request["destination_id"],
                        relocation_zone_id
                    )

                    duration = distance / 1000 / self.simInput.sim_scenario_conf["avg_relocation_speed"] * 3600

                    scooter_relocation = init_scooter_relocation(
                        relocated_vehicles,
                        booking_request["end_time"],
                        booking_request["destination_id"],
                        relocation_zone_id,
                        distance=distance,
                        duration=duration
                    )

                    if "save_history" in self.simInput.sim_general_conf:
                        if self.simInput.sim_general_conf["save_history"]:
                            self.sim_scooter_relocations += [scooter_relocation]

                    self.n_scooter_relocations += 1
                    self.tot_scooter_relocations_distance += distance
                    self.tot_scooter_relocations_duration += duration

        return relocated, scooter_relocation

    def choose_ending_zone(self, daytype=None, hour=None, n=1):

        ending_zone_ids = []
        n_dropped_vehicles_list = []
        technique = self.simInput.sim_scenario_conf["scooter_relocation_technique"]["end"]

        if technique == "kde_sampling":

            next_hour_kde = self.simInput.trip_kdes[daytype][(hour + 1) % 24]

            def base_round(x, base):
                if x < 0:
                    return 0
                elif x > base:
                    return base
                else:
                    return round(x)

            def gen_relocation_zone(kde):
                trip_sample = kde.sample()
                origin_i = base_round(trip_sample[0][0], len(self.simInput.grid_matrix.index) - 1)
                origin_j = base_round(trip_sample[0][1], len(self.simInput.grid_matrix.columns) - 1)

                return self.simInput.grid_matrix.loc[origin_i, origin_j]

            for i in range(n):
                relocation_zone_id = gen_relocation_zone(next_hour_kde)
                while relocation_zone_id not in self.simInput.valid_zones:
                    relocation_zone_id = gen_relocation_zone(next_hour_kde)
                ending_zone_ids.append(relocation_zone_id)
                n_dropped_vehicles_list.append(1)

        if technique == "aggregation":

            aggregation_by_zone = {
                k: len(v) / self.simInput.n_vehicles_sim for k, v in
                sorted(self.available_vehicles_dict.items(), key=lambda item: -len(item[1]))
            }

            for i in range(n):
                ending_zone_ids.append(aggregation_by_zone.popitem()[0])
                n_dropped_vehicles_list.append(1)

        if technique == "delta":  # demand proxy: origin scores, current status proxy: aggregation

            next_hour_origin_scores = self.simInput.origin_scores[daytype][(hour + 1) % 24]

            if "end_demand_weight" in self.simInput.sim_scenario_conf["scooter_relocation_technique"]:
                w1 = self.simInput.sim_scenario_conf["scooter_relocation_technique"]["end_demand_weight"]
            else:
                w1 = 0.5

            w2 = 1 - w1

            delta_by_zone = {
                k: (2 - abs(w1-w2)) * (w1 * next_hour_origin_scores[k] - w2 * (len(v) / self.simInput.n_vehicles_sim)) for k, v in
                self.available_vehicles_dict.items()
            }

            delta_by_zone = {
                k: v for k, v in
                sorted(delta_by_zone.items(), key=lambda item: item[1])
            }

            if "end_vehicles_factor" in self.simInput.sim_scenario_conf["scooter_relocation_technique"]:
                end_vehicles_factor = self.simInput.sim_scenario_conf["scooter_relocation_technique"]["end_vehicles_factor"]
            else:
                end_vehicles_factor = 1

            for i in range(n):
                item = delta_by_zone.popitem()
                n_dropped_vehicles = int(item[1] * end_vehicles_factor * self.simInput.n_vehicles_sim)
                if n_dropped_vehicles:
                    ending_zone_ids.append(item[0])
                    n_dropped_vehicles_list.append(n_dropped_vehicles)

        return ending_zone_ids, n_dropped_vehicles_list

    def choose_starting_zone(self, daytype=None, hour=None, n=1):

        starting_zone_ids = []
        n_picked_vehicles_list = []
        technique = self.simInput.sim_scenario_conf["scooter_relocation_technique"]["start"]

        if technique == "aggregation":

            aggregation_by_zone = {
                k: len(v) / self.simInput.n_vehicles_sim for k, v in
                sorted(self.available_vehicles_dict.items(), key=lambda item: len(item[1]))
            }

            for i in range(min(n, len(aggregation_by_zone))):
                starting_zone_ids.append(aggregation_by_zone.popitem()[0])
                n_picked_vehicles_list.append(1)

        if technique == "delta":  # demand proxy: origin scores, current status proxy: aggregation

            next_hour_origin_scores = self.simInput.origin_scores[daytype][(hour + 1) % 24]

            if "start_demand_weight" in self.simInput.sim_scenario_conf["scooter_relocation_technique"]:
                w1 = self.simInput.sim_scenario_conf["scooter_relocation_technique"]["start_demand_weight"]
            else:
                w1 = 0.5

            w2 = 1 - w1

            delta_by_zone = {
                k: w1 * next_hour_origin_scores[k] - w2 * (len(v) / self.simInput.n_vehicles_sim) for k, v in
                self.available_vehicles_dict.items()
            }

            delta_by_zone = {
                k: v for k, v in
                sorted(delta_by_zone.items(), key=lambda item: -item[1])
            }

            if "start_vehicles_factor" in self.simInput.sim_scenario_conf["scooter_relocation_technique"]:
                start_vehicles_factor = self.simInput.sim_scenario_conf["scooter_relocation_technique"]["start_vehicles_factor"]
            else:
                start_vehicles_factor = 1

            for i in range(n):
                item = delta_by_zone.popitem()
                n_picked_vehicles = int(abs(item[1]) * start_vehicles_factor * self.simInput.n_vehicles_sim)
                if n_picked_vehicles:
                    starting_zone_ids.append(item[0])
                    n_picked_vehicles_list.append(n_picked_vehicles)

        return starting_zone_ids, n_picked_vehicles_list

    def generate_relocation_schedule(self, daytype, hour):

        self.scheduled_scooter_relocations.clear()
        n_relocations = self.relocation_workers.capacity - self.relocation_workers.count  # free_workers

        starting_zone_ids, n_picked_vehicles_list = self.choose_starting_zone(daytype=daytype, hour=hour, n=n_relocations)
        ending_zone_ids, n_dropped_vehicles_list = self.choose_ending_zone(daytype=daytype, hour=hour, n=n_relocations)

        for i in range(min(n_relocations, len(starting_zone_ids), len(ending_zone_ids))):
            starting_zone_id = starting_zone_ids[i]
            ending_zone_id = ending_zone_ids[i]

            n_picked_vehicles = n_picked_vehicles_list[i]
            n_dropped_vehicles = n_dropped_vehicles_list[i]

            n_relocated_vehicles = min(
                n_picked_vehicles,
                n_dropped_vehicles,
            )

            if starting_zone_id not in self.scheduled_scooter_relocations:
                self.scheduled_scooter_relocations[starting_zone_id] = {}
            if ending_zone_id not in self.scheduled_scooter_relocations[starting_zone_id]:
                self.scheduled_scooter_relocations[starting_zone_id][ending_zone_id] = n_relocated_vehicles
            else:
                self.scheduled_scooter_relocations[starting_zone_id][ending_zone_id] += n_relocated_vehicles
