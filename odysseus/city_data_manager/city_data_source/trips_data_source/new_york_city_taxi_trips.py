import os
import datetime

import pandas as pd
from odysseus.utils.geospatial_utils import haversine

from odysseus.city_data_manager.city_data_source.trips_data_source.trips_data_source import TripsDataSource


class NewYorkCityTaxiTrips(TripsDataSource):

    def __init__(self, city_name):
        super().__init__(city_name, 'nyc_taxi', 'car')
        self.max_lon = -73.90
        self.min_lon = -74.04
        self.max_lat = 40.76
        self.min_lat = 40.66

    def load_raw(self, year, month):

        raw_trips_data_path = os.path.join(
            self.raw_data_path,
            "green_tripdata_" + "%s-%s"% (str(year), str(month).zfill(2)) + ".csv"
        )
        self.trips_df = pd.read_csv(raw_trips_data_path)
        return self.trips_df
