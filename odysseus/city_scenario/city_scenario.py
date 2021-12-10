import json
import pickle
import datetime

from odysseus.city_scenario.city_data_loader import CityDataLoader
from odysseus.utils.time_utils import *
from odysseus.utils.geospatial_utils import *
from odysseus.path_config.path_config import *

from odysseus.city_scenario.energymix_loader import EnergyMix
from odysseus.city_scenario.abstract_city_scenario import AbstractCityScenario


class CityScenario(AbstractCityScenario):

    def __init__(self, city_name, data_source_id, city_scenario_config=None, read_config_from_file=False, in_folder_name=None):

        super(CityScenario, self).__init__(city_name, data_source_id)

        if city_scenario_config:
            self.city_scenario_config = city_scenario_config
            self.folder_name = self.city_scenario_config["folder_name"]
        if read_config_from_file and in_folder_name:
            self.folder_name = in_folder_name
        else:
            raise IOError("Wrong arguments for CityScenario!")

        self.city_scenario_path = os.path.join(
            city_scenarios_path,
            city_name,
            self.folder_name
        )
        if read_config_from_file and in_folder_name:
            self.read_config_from_folder_name()

        self.bin_side_length = int(self.city_scenario_config["bin_side_length"])

    def init_train_test(
            self, start_year_train, start_month_train, end_year_train, end_month_train,
                 start_year_test, start_month_test, end_year_test, end_month_test
    ):

        self.loader = CityDataLoader(self.city_name, self.data_source_id)
        self.bookings_train, self.trips_origins_train, self.trips_destinations_train = \
            self.loader.read_year_month_range_data(
                start_month_train, start_year_train, end_month_train, end_year_train
            )
        self.bookings_train = self.get_input_bookings_filtered(self.bookings_train).dropna()

        self.bookings_test, self.trips_origins_test, self.trips_destinations_test = \
            self.loader.read_year_month_range_data(
                start_month_test, start_year_test, end_month_test, end_year_test
            )
        self.bookings_test = self.get_input_bookings_filtered(self.bookings_test).dropna()
        self.year_energy_mix = end_year_test
        self.tz = self.loader.tz

    def create_squared_city_grid(self):
        self.grid = get_city_grid_as_gdf(
            (
                min(self.trips_origins_train.start_longitude.min(), self.trips_destinations_train.end_longitude.min(),
                    self.trips_origins_test.start_longitude.min(), self.trips_destinations_test.end_longitude.min()),
                min(self.trips_origins_train.start_latitude.min(), self.trips_destinations_train.end_latitude.min(),
                    self.trips_origins_test.start_latitude.min(), self.trips_destinations_test.end_latitude.min()),
                max(self.trips_origins_train.start_longitude.max(), self.trips_destinations_train.end_longitude.max(),
                    self.trips_origins_test.start_longitude.max(), self.trips_destinations_test.end_longitude.max()),
                max(self.trips_origins_train.start_latitude.max(), self.trips_destinations_train.end_latitude.max(),
                    self.trips_origins_test.start_latitude.max(), self.trips_destinations_test.end_latitude.max())
            ),
            self.bin_side_length
        )
        self.grid_matrix = get_city_grid_as_matrix(
            (
                min(self.trips_origins_train.start_longitude.min(), self.trips_destinations_train.end_longitude.min(),
                    self.trips_origins_test.start_longitude.min(), self.trips_destinations_test.end_longitude.min()),
                min(self.trips_origins_train.start_latitude.min(), self.trips_destinations_train.end_latitude.min(),
                    self.trips_origins_test.start_latitude.min(), self.trips_destinations_test.end_latitude.min()),
                max(self.trips_origins_train.start_longitude.max(), self.trips_destinations_train.end_longitude.max(),
                    self.trips_origins_test.start_longitude.max(), self.trips_destinations_test.end_longitude.max()),
                max(self.trips_origins_train.start_latitude.max(), self.trips_destinations_train.end_latitude.max(),
                    self.trips_origins_test.start_latitude.max(), self.trips_destinations_test.end_latitude.max())
            ),
            self.bin_side_length
        )
        self.grid["zone_id"] = self.grid.index.values
        self.map_zones_on_trips(self.grid)
