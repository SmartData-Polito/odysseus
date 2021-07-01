import datetime

from odysseus.simulator.simulation.simulator import SharedMobilitySim
from odysseus.utils.time_utils import update_req_time_info
from odysseus.simulator.simulation_data_structures.booking_request import BookingRequest


class TraceDrivenSim (SharedMobilitySim):

    def create_booking_request_dict(self, booking_request_dict):

        self.update_time_info()
        booking_request_dict = update_req_time_info(booking_request_dict)
        return booking_request_dict

    def mobility_requests_generator(self):

        sim_timestamps = []

        for booking_request_dict in self.simInput.booking_requests_list:

            if booking_request_dict["origin_id"] in self.valid_zones\
                    and booking_request_dict["destination_id"] in self.valid_zones:

                booking_request_dict = self.create_booking_request_dict(booking_request_dict)
                sim_timestamps += [self.current_datetime]

                if self.simInput.supply_model_conf["scooter_relocation"] \
                        and self.simInput.supply_model_conf["scooter_relocation_strategy"] in ["predictive"]:
                    self.scooterRelocationStrategy.update_current_hour_stats(booking_request_dict)

                yield self.env.timeout(booking_request_dict["ia_timeout"])
                booking_request = BookingRequest(booking_request_dict)
                self.process_booking_request(booking_request)
