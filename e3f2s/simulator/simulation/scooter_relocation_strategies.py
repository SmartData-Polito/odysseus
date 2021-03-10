from collections import deque
import six
import sys
sys.modules['sklearn.externals.six'] = six
from mlrose import TSPOpt, genetic_alg

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

                    distance = get_od_distance(
                        self.simInput.grid,
                        max_soc_vehicle_zone,
                        relocation_zone_id
                    )

                    scooter_relocation = init_scooter_relocation(relocated_vehicles, booking_request["start_time"],
                                                                 [max_soc_vehicle_zone], [relocation_zone_id],
                                                                 distance, 0)

            else:

                relocation_zone_id = None

                if self.simInput.supply_model_conf["scooter_relocation_strategy"] in ["reactive_post_charge",
                                                                                      "reactive_post_trip"]:

                    scheduled_relocation = None
                    for proposed_relocation in self.scheduled_scooter_relocations:
                        if booking_request["destination_id"] in proposed_relocation["start"]:
                            scheduled_relocation = proposed_relocation

                    if scheduled_relocation:
                        self.scheduled_scooter_relocations.remove(scheduled_relocation)

                        relocation_zone_id, n_relocated_vehicles = scheduled_relocation["end"].popitem()

                        if relocated_vehicles is not None:
                            for i in range(
                                    len(relocated_vehicles),  # first vehicles are input vehicles
                                    min(
                                        n_relocated_vehicles,
                                        len(self.available_vehicles_dict[booking_request["destination_id"]])
                                    )):
                                relocated_vehicle = self.available_vehicles_dict[booking_request["destination_id"]].pop()
                                relocated_vehicles.append(relocated_vehicle)
                        else:
                            relocated_vehicles = []
                            for i in range(
                                    0,
                                    min(
                                        n_relocated_vehicles,
                                        len(self.available_vehicles_dict[booking_request["destination_id"]])
                                    )):
                                relocated_vehicle = self.available_vehicles_dict[booking_request["destination_id"]].pop()
                                relocated_vehicles.append(relocated_vehicle)

                else:
                    relocation_zone_ids, _ = self.choose_ending_zone(daytype=booking_request["daytype"],
                                                                     hour=booking_request["hour"])
                    relocation_zone_id = relocation_zone_ids[0]

                if relocation_zone_id and relocation_zone_id != booking_request["destination_id"] \
                        and relocated_vehicles:

                    relocated = True

                    distance = get_od_distance(
                        self.simInput.grid,
                        booking_request["destination_id"],
                        relocation_zone_id
                    )

                    duration = distance / 1000 / self.simInput.supply_model_conf["avg_relocation_speed"] * 3600

                    scooter_relocation = init_scooter_relocation(relocated_vehicles, booking_request["end_time"],
                                                                 [booking_request["destination_id"]],
                                                                 [relocation_zone_id],
                                                                 distance, duration)

        return relocated, scooter_relocation

    def choose_ending_zone(self, n=1, origin_scores_list=None, destination_scores_list=None, daytype=None, hour=None):
        """
        Chooses n ending zones given a list of origin and destination scores, according to the selected zone selection
        technique. If the technique defines a priority (e.g.: vehicles aggregation or Delta value), returned lists are
        ordered by relocation priority.
        :param n: Maximum number of zones to be selected as ending zones.
        :param origin_scores_list: List of origin scores. It is required by 'Delta' technique. Each element of this list
        should correspond to a dictionary of probabilities for a given hour. Each value of this dictionary should be the
        probability for a given zone to be selected as an origin zone for a trip.
        :param destination_scores_list: List of destination scores. It is required by 'Delta' technique. Its structure
        is similar to origin_scores_list. See the latter for further details.
        :param daytype: Current simulated type of day (i.e.: 'weekday', 'weekend'). Required by 'kde_sampling' technique.
        :param hour: Current simulated hour. Required by 'kde_sampling' technique.
        :return: A list of proposed ending zones and a list of proposed numbers of vehicles to be dropped off into such
        zones. If the technique defines a priority, returned lists are ordered by relocation priority.
        """
        ending_zone_ids = []
        n_dropped_vehicles_list = []
        technique = dict(self.simInput.supply_model_conf["scooter_relocation_technique"])["end"]

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
                origin_id = gen_relocation_zone(next_hour_kde)
                while (origin_id not in self.simInput.valid_zones) or (origin_id in self.starting_zone_ids):
                    origin_id = gen_relocation_zone(next_hour_kde)
                ending_zone_ids.append(origin_id)
                n_dropped_vehicles_list.append(1)

        if technique == "aggregation":

            n_vehicles_by_zone = {
                k: len(v) for k, v in
                sorted(self.available_vehicles_dict.items(), key=lambda item: -len(item[1]))
            }

            for i in range(min(n, len(n_vehicles_by_zone))):
                ending_zone_ids.append(n_vehicles_by_zone.popitem()[0])
                n_dropped_vehicles_list.append(1)

        if technique == "delta":

            if "end_demand_weight" in dict(self.simInput.supply_model_conf["scooter_relocation_technique"]):
                demand_weight = dict(self.simInput.supply_model_conf["scooter_relocation_technique"])["end_demand_weight"]
            else:
                demand_weight = 0.5

            delta_by_zone = self.compute_delta(origin_scores_list, destination_scores_list, demand_weight)

            delta_by_zone = {
                k: v for k, v in
                sorted(delta_by_zone.items(), key=lambda item: item[1])
            }

            if "end_vehicles_factor" in dict(self.simInput.supply_model_conf["scooter_relocation_technique"]):
                end_vehicles_factor = dict(self.simInput.supply_model_conf["scooter_relocation_technique"])["end_vehicles_factor"]
            else:
                end_vehicles_factor = 1

            for i in range(min(n, len(delta_by_zone))):
                zone, delta = delta_by_zone.popitem()
                n_dropped_vehicles = int(delta * end_vehicles_factor * self.simInput.n_vehicles_sim)
                if n_dropped_vehicles > 0:
                    ending_zone_ids.append(zone)
                    n_dropped_vehicles_list.append(n_dropped_vehicles)

        return ending_zone_ids, n_dropped_vehicles_list

    def choose_starting_zone(self, n=1, origin_scores_list=None, destination_scores_list=None):
        """
        Chooses n starting zones given a list of origin and destination scores, according to the selected zone selection
        technique. If the technique defines a priority (e.g.: vehicles aggregation or Delta value), returned lists are
        ordered by relocation priority.
        :param n: Maximum number of zones to be selected as starting zones.
        :param origin_scores_list: List of origin scores. It is required by 'Delta' technique. Each element of this list
        should correspond to a dictionary of probabilities for a given hour. Each value of this dictionary should be the
        probability for a given zone to be selected as an origin zone for a trip.
        :param destination_scores_list: List of destination scores. It is required by 'Delta' technique. Its structure
        is similar to origin_scores_list. See the latter for further details.
        :return: A list of proposed starting zones and a list of proposed numbers of vehicles to be picked up from such
        zones. If the technique defines a priority, returned lists are ordered by relocation priority.
        """
        starting_zone_ids = []
        n_picked_vehicles_list = []
        technique = dict(self.simInput.supply_model_conf["scooter_relocation_technique"])["start"]

        if technique == "aggregation":

            n_vehicles_by_zone = {
                k: len(v) for k, v in
                sorted(self.available_vehicles_dict.items(), key=lambda item: len(item[1]))
            }

            for i in range(min(n, len(n_vehicles_by_zone))):
                starting_zone_ids.append(n_vehicles_by_zone.popitem()[0])
                n_picked_vehicles_list.append(1)

        if technique == "delta":

            if "start_demand_weight" in dict(self.simInput.supply_model_conf["scooter_relocation_technique"]):
                demand_weight = dict(self.simInput.supply_model_conf["scooter_relocation_technique"])["start_demand_weight"]
            else:
                demand_weight = 0.5

            delta_by_zone = self.compute_delta(origin_scores_list, destination_scores_list, demand_weight)

            delta_by_zone = {
                k: v for k, v in
                sorted(delta_by_zone.items(), key=lambda item: -item[1])
            }

            if "start_vehicles_factor" in dict(self.simInput.supply_model_conf["scooter_relocation_technique"]):
                start_vehicles_factor = dict(self.simInput.supply_model_conf["scooter_relocation_technique"])["start_vehicles_factor"]
            else:
                start_vehicles_factor = 1

            for i in range(min(n, len(delta_by_zone))):
                zone, delta = delta_by_zone.popitem()
                n_picked_vehicles = int(-delta * start_vehicles_factor * self.simInput.n_vehicles_sim)
                if n_picked_vehicles > 0:
                    starting_zone_ids.append(zone)
                    n_picked_vehicles_list.append(n_picked_vehicles)

        return starting_zone_ids, n_picked_vehicles_list

    def generate_relocation_schedule(self, daytype, hour):
        """
        It generates a relocation schedule for a given hour of a day of a given type (i.e.: 'weekday', 'weekend').
        If the relocation strategy requires it, once generation is finished, the relocation process is automatically
        triggered.
        :param daytype: Current simulated type of day (i.e.: 'weekday', 'weekend')
        :param hour: Current simulated hour.
        :return: void
        """

        self.scheduled_scooter_relocations.clear()

        if "window_width" in dict(self.simInput.supply_model_conf["scooter_relocation_technique"]):
            window_width = dict(self.simInput.supply_model_conf["scooter_relocation_technique"])["window_width"]
        else:
            window_width = 1

        origin_scores_list = []
        destination_scores_list = []

        if self.simInput.supply_model_conf["scooter_relocation_strategy"] == "predictive":

            if self.current_hour_n_bookings:
                self.past_hours_n_bookings.append(self.current_hour_n_bookings)
                self.past_hours_origin_counts.append(self.current_hour_origin_count)
                self.past_hours_destination_counts.append(self.current_hour_destination_count)

                if len(self.past_hours_n_bookings) > window_width:
                    self.past_hours_n_bookings.pop(0)
                    self.past_hours_origin_counts.pop(0)
                    self.past_hours_destination_counts.pop(0)

                for i in range(len(self.past_hours_n_bookings)):
                    past_n_bookings = self.past_hours_n_bookings[i]
                    past_origin_count = self.past_hours_origin_counts[i]
                    past_destination_count = self.past_hours_destination_counts[i]

                    past_origin_scores = {}
                    past_destination_scores = {}
                    for zone in self.simInput.valid_zones:
                        if zone in past_origin_count:
                            past_origin_scores[zone] = past_origin_count[zone] / past_n_bookings
                        else:
                            past_origin_scores[zone] = 0
                        if zone in past_destination_count:
                            past_destination_scores[zone] = past_destination_count[zone] / past_n_bookings
                        else:
                            past_destination_scores[zone] = 0

                    origin_scores_list.append(past_origin_scores)
                    destination_scores_list.append(past_destination_scores)
            else:
                return

            self.reset_current_hour_stats()

        else:
            origin_scores = self.simInput.origin_scores
            destination_scores = self.simInput.destination_scores

            for i in range(window_width):
                origin_scores_list.append(origin_scores[daytype][(hour + 1 + i) % 24])
                destination_scores_list.append(destination_scores[daytype][(hour + 1 + i) % 24])

        n_relocations = int(len(self.available_vehicles_dict) / 2)  # an upper bound
        if self.simInput.supply_model_conf["scooter_relocation_strategy"] in ["proactive", "predictive"]:
            n_free_workers = self.relocation_workers_resource.capacity - self.relocation_workers_resource.count
            n_relocations = min(n_relocations, n_free_workers)

        self.starting_zone_ids, self.n_picked_vehicles_list = self.choose_starting_zone(
            n=n_relocations,
            origin_scores_list=origin_scores_list,
            destination_scores_list=destination_scores_list
        )
        self.ending_zone_ids, self.n_dropped_vehicles_list = self.choose_ending_zone(
            n=n_relocations,
            origin_scores_list=origin_scores_list,
            destination_scores_list=destination_scores_list,
            daytype=daytype, hour=hour
        )

        if self.simInput.supply_model_conf["scooter_relocation_strategy"] in ["proactive", "predictive"] \
                and "relocation_capacity" in self.simInput.supply_model_conf:
            relocation_capacity = self.simInput.supply_model_conf["relocation_capacity"]

            starting_zone_ids_deque = deque(self.starting_zone_ids)
            n_picked_vehicles_deque = deque(self.n_picked_vehicles_list)
            ending_zone_ids_deque = deque(self.ending_zone_ids)
            n_dropped_vehicles_deque = deque(self.n_dropped_vehicles_list)

            try:
                starting_zone_id = starting_zone_ids_deque.popleft()
                n_picked_vehicles = n_picked_vehicles_deque.popleft()
                ending_zone_id = ending_zone_ids_deque.popleft()
                n_dropped_vehicles = n_dropped_vehicles_deque.popleft()
            except IndexError:
                return

            empty_deque = False
            for i in range(n_relocations):
                if empty_deque:
                    break

                residual_capacity = relocation_capacity
                scheduled_relocation = {
                    "start": {},
                    "end": {}
                }

                while residual_capacity > 0 and not empty_deque:
                    try:
                        new_starting_zone_id = starting_zone_id
                        new_n_picked_vehicles = n_picked_vehicles
                        new_ending_zone_id = ending_zone_id
                        new_n_dropped_vehicles = n_dropped_vehicles

                        if n_picked_vehicles > residual_capacity:
                            # Try to consume all residual capacity
                            if residual_capacity > n_dropped_vehicles:
                                # Ending zone needs are satisfied before
                                n_relocated_vehicles = n_dropped_vehicles
                                new_ending_zone_id = ending_zone_ids_deque.popleft()
                                new_n_dropped_vehicles = n_dropped_vehicles_deque.popleft()

                            elif residual_capacity < n_dropped_vehicles:
                                # Residual capacity is totally consumed before
                                n_relocated_vehicles = residual_capacity
                                new_n_picked_vehicles -= residual_capacity
                                new_n_dropped_vehicles -= residual_capacity

                            else:
                                # Ending zone needs coincide with residual capacity
                                n_relocated_vehicles = residual_capacity
                                new_n_picked_vehicles = residual_capacity
                                new_ending_zone_id = ending_zone_ids_deque.popleft()
                                new_n_dropped_vehicles = n_dropped_vehicles_deque.popleft()

                        else:
                            # Try to satisfy all starting zone needs
                            if n_picked_vehicles > n_dropped_vehicles:
                                # Ending zone needs are satisfied before
                                n_relocated_vehicles = n_dropped_vehicles
                                new_n_picked_vehicles -= n_dropped_vehicles
                                new_ending_zone_id = ending_zone_ids_deque.popleft()
                                new_n_dropped_vehicles = n_dropped_vehicles_deque.popleft()

                            elif n_picked_vehicles < n_dropped_vehicles:
                                # Starting zone needs are satisfied before
                                n_relocated_vehicles = n_picked_vehicles
                                new_n_dropped_vehicles -= n_picked_vehicles
                                new_starting_zone_id = starting_zone_ids_deque.popleft()
                                new_n_picked_vehicles = n_picked_vehicles_deque.popleft()

                            else:
                                # Ending zone needs coincide with starting zone needs
                                n_relocated_vehicles = n_picked_vehicles
                                new_starting_zone_id = starting_zone_ids_deque.popleft()
                                new_n_picked_vehicles = n_picked_vehicles_deque.popleft()
                                new_ending_zone_id = ending_zone_ids_deque.popleft()
                                new_n_dropped_vehicles = n_dropped_vehicles_deque.popleft()

                    except IndexError:
                        # Ran out of starting or ending zones
                        empty_deque = True
                        break

                    finally:
                        if starting_zone_id not in scheduled_relocation["start"]:
                            scheduled_relocation["start"][starting_zone_id] = n_relocated_vehicles
                        else:
                            scheduled_relocation["start"][starting_zone_id] += n_relocated_vehicles

                        scheduled_relocation["end"][ending_zone_id] = n_relocated_vehicles

                        residual_capacity -= n_relocated_vehicles

                        starting_zone_id = new_starting_zone_id
                        n_picked_vehicles = new_n_picked_vehicles
                        ending_zone_id = new_ending_zone_id
                        n_dropped_vehicles = new_n_dropped_vehicles

                self.scheduled_scooter_relocations.append(scheduled_relocation)

        else:

            for i in range(min(n_relocations, len(self.starting_zone_ids), len(self.ending_zone_ids))):
                starting_zone_id = self.starting_zone_ids[i]
                ending_zone_id = self.ending_zone_ids[i]

                n_picked_vehicles = self.n_picked_vehicles_list[i]
                n_dropped_vehicles = self.n_dropped_vehicles_list[i]

                tot_relocated_vehicles = min(
                    n_picked_vehicles,
                    n_dropped_vehicles,
                )

                scheduled_relocation = {
                    "start": {starting_zone_id: tot_relocated_vehicles},
                    "end": {ending_zone_id: tot_relocated_vehicles}
                }

                self.scheduled_scooter_relocations.append(scheduled_relocation)

        if self.simInput.supply_model_conf["scooter_relocation_strategy"] in ["proactive", "predictive"]:
            free_workers = [worker for worker in self.relocation_workers if not worker.busy]

            # Trigger immediately the relocation process
            for i in range(min(n_relocations, len(self.scheduled_scooter_relocations))):
                worker = free_workers[i]
                scheduled_relocation = self.scheduled_scooter_relocations[i]

                collection_path = self.compute_shortest_path(
                    worker.current_position,
                    scheduled_relocation["start"].keys()
                )
                distribution_path = self.compute_shortest_path(
                    collection_path[-1],
                    scheduled_relocation["end"].keys()
                )

                self.env.process(self.relocate_scooter_multiple_zones(scheduled_relocation,
                                                                      collection_path, distribution_path,
                                                                      worker))

    def compute_delta(self, origin_scores_list, destination_scores_list, demand_weight=0.5):

        window_width = len(origin_scores_list)

        w1 = demand_weight
        w2 = 1 - w1

        delta_by_zone = {}
        for zone, vehicles in self.available_vehicles_dict.items():
            demand_prediction = 0
            for i in range(window_width):
                demand_prediction += origin_scores_list[i][zone]
                demand_prediction -= destination_scores_list[i][zone]
            demand_prediction /= window_width
            delta = w1 * demand_prediction - w2 * (len(vehicles) / self.simInput.n_vehicles_sim)
            delta_by_zone[zone] = delta

        return delta_by_zone

    def compute_shortest_path(self, starting_zone_id, other_zone_ids):
        zones = [starting_zone_id]
        [zones.append(zone) for zone in other_zone_ids]

        coords_list = []
        for zone in zones:
            zone_column = int(np.floor(
                zone / self.simInput.grid_matrix.shape[0]
            ))
            zone_row = int(
                zone - zone_column * self.simInput.grid_matrix.shape[0]
            )
            coords_list.append((zone_column, zone_row))

        problem = TSPOpt(length=len(coords_list), coords=coords_list, maximize=False)
        best_path, _ = genetic_alg(problem, max_iters=10, random_state=2)

        best_path = deque(best_path)
        starting_point = best_path[0]
        while starting_point != 0:  # Starting point is not worker position
            best_path.rotate(1)
            starting_point = best_path[0]

        return [zones[i] for i in list(best_path)]
