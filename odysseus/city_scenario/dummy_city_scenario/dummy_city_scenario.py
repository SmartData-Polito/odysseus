import json
import os
import pickle
import datetime

from odysseus.city_scenario.city_data_loader import CityDataLoader
from odysseus.utils.time_utils import *
from odysseus.utils.geospatial_utils import *
from odysseus.path_config.path_config import *

from odysseus.city_scenario.energymix_loader import EnergyMix
from odysseus.mobility_event.booking_request import BookingRequest
from odysseus.city_scenario.abstract_city_scenario import AbstractCityScenario


class DummyCityScenario(AbstractCityScenario):

    def __init__(
            self, dummy_city_name, bin_side_length
    ):

        super(DummyCityScenario, self).__init__(dummy_city_name)
        self.bin_side_length = bin_side_length
        self.bookings_train = pd.read_csv(os.path.join(root_dummy_data_path, self.city_name, "dummy_train.csv"))
        self.bookings_test = pd.read_csv(os.path.join(root_dummy_data_path, self.city_name, "dummy_test.csv"))
        self.create_squared_city_grid(
            max(
                self.bookings_train.origin_j.max(), self.bookings_test.origin_j.max(),
                self.bookings_train.destination_j.max(), self.bookings_test.destination_j.max(),
            ) + 1,
            max(
                self.bookings_train.origin_i.max(), self.bookings_test.origin_i.max(),
                self.bookings_train.destination_i.max(), self.bookings_test.destination_i.max(),
            ) + 1,
            self.bin_side_length
        )

    def create_squared_city_grid(self, n_zones_x, n_zones_y, bin_side_length):
        print(n_zones_x, n_zones_y)
        self.bin_side_length = bin_side_length
        # TODO -> check real conversion factor
        #METERS_TO_DEGREES = 0.000082
        total_bounds = (
            0, 0, n_zones_x * bin_side_length, n_zones_y * bin_side_length
        )
        self.grid = get_city_grid_as_gdf(total_bounds, bin_side_length, "dummy_crs")
        self.grid_matrix = get_city_grid_as_matrix(total_bounds, bin_side_length, "dummy_crs")

    # def add_booking_request(self, train_or_test, origin_id, destination_id, start_time, end_time):
    #     if train_or_test == "train":
    #         self.bookings_train = pd.concat([
    #             self.bookings_train,
    #             BookingRequest(origin_id, destination_id, start_time, end_time)
    #         ])
    #     elif train_or_test == "test":
    #         self.bookings_test = pd.concat([
    #             self.bookings_test,
    #             BookingRequest(origin_id, destination_id, start_time, end_time)
    #         ])
    #     else:
    #         raise Exception("Possible choices are 'test' or 'train'")
