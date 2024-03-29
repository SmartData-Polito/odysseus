import datetime

from odysseus.simulator.simulation_data_structures.sim_event import SimEvent
from odysseus.utils.bookings_utils import *


class SimBooking(SimEvent):

    def __init__(
            self, env, booking_request, chosen_origin, chosen_destination, vehicle,
            orography_factor=1.4
    ):

        super().__init__(env, "booking")
        self.booking_request = booking_request
        self.booking_request_dict = self.booking_request.booking_request_dict.copy()
        self.booking_dict = self.booking_request_dict.copy()
        self.booking_dict["req_origin_id"] = self.booking_dict["origin_id"]
        self.booking_dict["req_destination_id"] = self.booking_dict["destination_id"]
        self.chosen_origin = chosen_origin
        self.chosen_destination = chosen_destination
        self.booking_dict["origin_id"] = self.chosen_origin.zone_id
        self.booking_dict["destination_id"] = self.chosen_destination.zone_id

        # COMPUTING DISTANCES WITH GEOPANDAS INSIDE THE SIMULATION IS VERY EXPENSIVE
        # TODO -> solve case when euclidean_distance = 0 (two way trips)
        # self.booking_dict["euclidean_distance"] = self.booking_request.sim_input.distance_matrix.loc[
        #     self.booking_dict["origin_id"], self.booking_dict["destination_id"]
        # ] + 1
        # self.booking_dict["driving_distance"] = self.booking_dict["euclidean_distance"] * orography_factor
        # self.booking_dict = get_distances(self.booking_dict, grid)
        # self.booking_dict = get_walking_distances(self.booking_dict, grid)

        self.booking_dict["start_soc"] = vehicle.soc.level
        self.booking_dict["plate"] = vehicle.plate
        self.vehicle = vehicle

    def execute_booking(self):

        self.chosen_origin.remove_vehicle(self.booking_dict["start_time"])

        yield self.env.process(self.vehicle.booking(self.booking_dict))

        self.chosen_destination.add_vehicle(
            self.booking_dict["start_time"] + datetime.timedelta(seconds=self.booking_dict['duration'])
        )
        self.booking_dict["end_soc"] = self.vehicle.soc.level
