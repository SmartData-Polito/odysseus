import datetime
import itertools

import numpy as np

from odysseus.simulator.simulation.simulator import SharedMobilitySim

from odysseus.simulator.simulation_data_structures.sim_booking_request import SimBookingRequest
from odysseus.utils.bookings_utils import *

np.random.seed(44)


class ModelDrivenSim(SharedMobilitySim):

    def init_demand_data_structures(self):

        self.booking_request_arrival_rates = self.sim_input.request_rates
        self.trip_kdes = self.sim_input.trip_kdes
        self.valid_zones = self.sim_input.valid_zones
        self.update_demand_data_structures()

    def update_demand_data_structures(self):

        self.current_arrival_rate = self.booking_request_arrival_rates[self.current_daytype][self.current_hour]
        self.current_trip_kde = self.trip_kdes[self.current_daytype][self.current_hour]

    def create_booking_request_dict(self, timeout):

        booking_request_dict = dict()

        booking_request_dict["ia_timeout"] = timeout
        booking_request_dict["start_time"] = self.current_datetime
        booking_request_dict["date"] = self.current_datetime.date()
        booking_request_dict["weekday"] = self.current_weekday
        booking_request_dict["daytype"] = self.current_daytype
        booking_request_dict["hour"] = self.current_hour

        def base_round(x, base):
            if x < 0:
                return 0
            elif x > base:
                return base
            else:
                return round(x)

        trip_sample = self.current_trip_kde.sample()
        origin_i = base_round(trip_sample[0][0], len(self.sim_input.grid_matrix.index) - 1)
        origin_j = base_round(trip_sample[0][1], len(self.sim_input.grid_matrix.columns) - 1)
        destination_i = base_round(trip_sample[0][2], len(self.sim_input.grid_matrix.index) - 1)
        destination_j = base_round(trip_sample[0][3], len(self.sim_input.grid_matrix.columns) - 1)

        booking_request_dict["origin_id"] = self.sim_input.grid_matrix.loc[origin_i, origin_j]
        booking_request_dict["destination_id"] = self.sim_input.grid_matrix.loc[destination_i, destination_j]
        booking_request_dict["origin_id"] = self.closest_valid_zone.loc[booking_request_dict["origin_id"]]
        booking_request_dict["destination_id"] = self.closest_valid_zone.loc[booking_request_dict["destination_id"]]

        booking_request_dict = get_distances(
            booking_request_dict, self.sim_input.grid, self.sim_input.supply_model.city_scenario.bin_side_length
        )

        booking_request_dict["duration"] = booking_request_dict["driving_distance"] / (
                self.sim_input.avg_speed_kmh_mean / 3.6
        )
        booking_request_dict["end_time"] = self.current_datetime + datetime.timedelta(
            seconds=booking_request_dict["duration"]
        )

        return booking_request_dict

    def mobility_requests_generator(self):

        for i in itertools.count():

            timeout_sec = (
                np.random.exponential(
                    1 / self.sim_input.demand_model_conf["requests_rate_factor"] / self.current_arrival_rate
                )
            )

            # print(self.current_datetime, self.n_booking_requests)

            if timeout_sec < 60 * 60:
                yield self.env.timeout(timeout_sec)
                booking_request_dict = self.create_booking_request_dict(timeout_sec)
                booking_request = SimBookingRequest(
                    self.env, self.sim_input, self.vehicles_list, booking_request_dict
                )
                self.process_booking_request(booking_request)
            else:
                yield self.env.timeout(60 * 60)

            self.update_time_info()
            self.update_demand_data_structures()
