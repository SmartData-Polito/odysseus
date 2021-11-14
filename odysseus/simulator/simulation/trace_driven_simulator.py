import datetime

from odysseus.simulator.simulation.simulator import SharedMobilitySim
from odysseus.utils.time_utils import update_req_time_info
from odysseus.simulator.simulation_data_structures.booking_request import BookingRequest
from odysseus.utils.bookings_utils import *


class TraceDrivenSim (SharedMobilitySim):

    def create_booking_request_dict(self, booking_request_dict):

        self.update_time_info()
        booking_request_dict = update_req_time_info(booking_request_dict)
        return booking_request_dict

    def mobility_requests_generator(self):

        sim_timestamps = []

        for booking_request_dict in self.sim_input.booking_requests_list[:100]:

            if booking_request_dict["origin_id"] in self.valid_zones\
                    and booking_request_dict["destination_id"] in self.valid_zones:

                booking_request_dict = self.create_booking_request_dict(booking_request_dict)
                sim_timestamps += [self.current_datetime]

                if self.sim_input.supply_model_conf_grid["scooter_relocation"] \
                        and self.sim_input.supply_model_conf_grid["scooter_relocation_strategy"] in ["predictive"]:
                    self.scooterRelocationStrategy.update_current_hour_stats(booking_request_dict)

                yield self.env.timeout(booking_request_dict["ia_timeout"])
                booking_request = BookingRequest(
                    self.env, self.sim_input, self.vehicles_list, booking_request_dict
                )
                self.process_booking_request(booking_request)
