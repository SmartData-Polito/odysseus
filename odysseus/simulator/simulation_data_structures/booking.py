from odysseus.simulator.simulation_data_structures.sim_event import SimEvent
from odysseus.utils.bookings_utils import *


class Booking(SimEvent):

    def __init__(self, booking_request_dict, chosen_zone_id, grid):

        super().__init__("booking")

        self.booking_request_dict = booking_request_dict
        self.booking_dict = booking_request_dict.copy()
        self.booking_dict["origin_id"] = chosen_zone_id
        self.booking_dict = get_distances(
            self.booking_dict, grid,
        )
