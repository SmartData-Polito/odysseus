import datetime
import itertools

import numpy as np

# from odysseus.utils.vehicle_utils import get_soc_delta
# from odysseus.utils.vehicle_utils import soc_to_kwh
from odysseus.utils.geospatial_utils import get_od_distance
from odysseus.simulator.simulation.simulator import SharedMobilitySim

# from odysseus.data_structures.vehicle import Vehicle

np.random.seed(44)


class ModelDrivenSim(SharedMobilitySim):

    def init_data_structures(self):

        self.booking_request_arrival_rates = self.simInput.request_rates
        self.trip_kdes = self.simInput.trip_kdes
        self.valid_zones = self.simInput.valid_zones
        self.update_data_structures()

    def update_time_info(self):

        self.hours_spent += 1

        self.current_datetime = self.start + datetime.timedelta(seconds=self.env.now)
        if self.current_hour != self.current_datetime.hour:
            self.current_hour = self.current_datetime.hour
            self.update_relocation_schedule = True
        self.current_weekday = self.current_datetime.weekday()
        if self.current_weekday in [5, 6]:
            self.current_daytype = "weekend"
        else:
            self.current_daytype = "weekday"

        if self.update_relocation_schedule \
                and self.simInput.sim_scenario_conf["scooter_relocation"] \
                and self.simInput.sim_scenario_conf["scooter_relocation_strategy"] in ["proactive",
                                                                                       "reactive_post_charge",
                                                                                       "reactive_post_trip",
                                                                                       "predictive"]:
            self.scooterRelocationStrategy.generate_relocation_schedule(self.current_datetime, self.current_daytype,
                                                                        self.current_hour)
            self.update_relocation_schedule = False

        if self.update_relocation_schedule \
                and self.simInput.sim_scenario_conf["vehicle_relocation"] \
                and "vehicle_relocation_scheduling" in self.simInput.sim_scenario_conf.keys() \
                and self.simInput.sim_scenario_conf["vehicle_relocation_scheduling"]:
            self.vehicleRelocationStrategy.generate_relocation_schedule(self.current_datetime, self.current_daytype,
                                                                        self.current_hour)
            self.update_relocation_schedule = False

    def update_data_structures(self):

        self.current_arrival_rate = self.booking_request_arrival_rates[self.current_daytype][self.current_hour]
        self.current_trip_kde = self.trip_kdes[self.current_daytype][self.current_hour]

    def create_booking_request(self, timeout):

        booking_request = {}

        booking_request["ia_timeout"] = timeout
        booking_request["start_time"] = self.current_datetime
        booking_request["date"] = self.current_datetime.date()
        booking_request["weekday"] = self.current_weekday
        booking_request["daytype"] = self.current_daytype
        booking_request["hour"] = self.current_hour

        def base_round(x, base):
            if x < 0:
                return 0
            elif x > base:
                return base
            else:
                return round(x)

        trip_sample = self.current_trip_kde.sample()
        origin_i = base_round(trip_sample[0][0], len(self.simInput.grid_matrix.index) - 1)
        origin_j = base_round(trip_sample[0][1], len(self.simInput.grid_matrix.columns) - 1)
        destination_i = base_round(trip_sample[0][2], len(self.simInput.grid_matrix.index) - 1)
        destination_j = base_round(trip_sample[0][3], len(self.simInput.grid_matrix.columns) - 1)

        booking_request["origin_id"] = self.simInput.grid_matrix.loc[origin_i, origin_j]
        booking_request["destination_id"] = self.simInput.grid_matrix.loc[destination_i, destination_j]
        booking_request["origin_id"] = self.closest_valid_zone.loc[booking_request["origin_id"]]
        booking_request["destination_id"] = self.closest_valid_zone.loc[booking_request["destination_id"]]

        booking_request["euclidean_distance"] = get_od_distance(
            self.simInput.grid,
            booking_request["origin_id"],
            booking_request["destination_id"]
        )

        if booking_request["euclidean_distance"] == 0:
            booking_request["euclidean_distance"] = self.simInput.demand_model_config["bin_side_length"]

        booking_request["driving_distance"] = booking_request["euclidean_distance"] * 1.4
        booking_request["duration"] = abs(booking_request["driving_distance"] / (
                (self.simInput.avg_speed_kmh_mean) / 3.6  # + np.random.normal(
            # 	self.simInput.avg_speed_kmh_std, self.simInput.avg_speed_kmh_std / 2
            # )) / 3.6
        ))
        booking_request["end_time"] = self.current_datetime + datetime.timedelta(
            seconds=booking_request["duration"]
        )
        # booking_request["soc_delta"] = -Vehicle.consumption_to_percentage(Vehicle.distance_to_consumption(booking_request["driving_distance"] / 1000))
        # booking_request["soc_delta_kwh"] = soc_to_kwh(booking_request["soc_delta"])
        self.process_booking_request(booking_request)

    def mobility_requests_generator(self):

        for i in itertools.count():

            timeout_sec = (
                np.random.exponential(
                    1 / self.simInput.sim_scenario_conf["requests_rate_factor"] / self.current_arrival_rate
                )
            )

            if timeout_sec < 60 * 60:
                yield self.env.timeout(timeout_sec)
                self.create_booking_request(timeout_sec)
            else:
                yield self.env.timeout(60 * 60)

            self.update_time_info()
            self.update_data_structures()
