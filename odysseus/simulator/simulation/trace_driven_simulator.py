import datetime

from odysseus.simulator.simulation.simulator import SharedMobilitySim
from odysseus.utils.time_utils import update_req_time_info
from odysseus.simulator.simulation_data_structures.sim_booking_request import SimBookingRequest
from odysseus.utils.bookings_utils import *


class TraceDrivenSim (SharedMobilitySim):

    def create_booking_request_dict(self, booking_request_dict):

        self.update_time_info()
        booking_request_dict = update_req_time_info(booking_request_dict)
        return booking_request_dict

    def mobility_requests_generator(self):

        sim_timestamps = []

        print(datetime.datetime.now(), "Simulation started ...")

        for booking_request_dict in self.sim_input.booking_requests_list:

            if booking_request_dict["origin_id"] in self.valid_zones\
                    and booking_request_dict["destination_id"] in self.valid_zones:

                booking_request_dict = self.create_booking_request_dict(booking_request_dict)
                sim_timestamps += [self.current_datetime]

                if self.sim_input.supply_model_conf["relocation"] \
                        and self.sim_input.supply_model_conf["relocation_strategy"] in ["predictive"]:
                    self.relocation_strategy.update_current_hour_stats(booking_request_dict)

                yield self.env.timeout(booking_request_dict["ia_timeout"])

                booking_request = SimBookingRequest(
                    self.env, self.sim_input, self.vehicles_list, booking_request_dict
                )
                self.process_booking_request(booking_request)
