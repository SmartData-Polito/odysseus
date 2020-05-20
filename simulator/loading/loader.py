import os
import pandas as pd

from city_data_manager.config.config import root_data_path


class Loader ():
    
    def __init__ (self, city, data_source_id, year, month, bin_side_length):
        
        self.city = city
        self.year = year
        self.month = month
        self.data_source_id = data_source_id

        self.norm_data_path = os.path.join(
            root_data_path,
            self.city,
            "_".join([str(year), str(month)]),
            data_source_id,
            str(bin_side_length),

        )

    def read_origins_destinations (self):
        path = os.path.join(
            self.norm_data_path,
            "points",
            "origins.pickle"
        )
        self.trips_origins = pd.read_pickle(path)
        path = os.path.join(
            self.norm_data_path,
            "points",
            "destinations.pickle"
        )
        self.trips_destinations = pd.read_pickle(path)
        return self.trips_origins, self.trips_destinations

    def read_trips (self):

        path = os.path.join(
            self.norm_data_path,
            "od_trips",
            "od_trips.pickle"
        )
        self.bookings = pd.read_pickle(path)

        return self.bookings
