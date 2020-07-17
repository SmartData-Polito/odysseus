import os
import geopandas as gpd
import pandas as pd
import shapely

from e3f2s.city_data_manager.config.config import root_data_path


class Loader:
    
    def __init__(self, city, data_source_id, year, month, bin_side_length):
        
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

        # path = os.path.join(
        #     self.norm_data_path,
        #     "points",
        #     "origins.pickle"
        # )
        # self.trips_origins = pd.read_pickle(path)
        #
        # path = os.path.join(
        #     self.norm_data_path,
        #     "points",
        #     "destinations.pickle"
        # )
        # self.trips_destinations = pd.read_pickle(path)

        #print(self.bookings[[
        #    "start_longitude", "start_latitude",
        #    "end_longitude", "end_latitude"
        #]])

        trips_origins = self.bookings.copy()
        trips_destinations = self.bookings.copy()

        trips_origins["geometry"] = trips_origins.apply(
            lambda row: shapely.geometry.Point(row["start_latitude"], row["start_longitude"]), axis=1
        )
        trips_destinations["geometry"] = trips_destinations.apply(
            lambda row: shapely.geometry.Point(row["end_latitude"], row["end_longitude"]), axis=1
        )
        self.trips_origins = gpd.GeoDataFrame(trips_origins)
        #print(self.trips_origins.geometry)
        self.trips_origins.crs = "epsg:4326"
        self.trips_origins = self.trips_origins.to_crs("epsg:3857")
        #print(self.trips_origins.geometry)
        self.trips_destinations = gpd.GeoDataFrame(trips_destinations)
        #print(self.trips_destinations.geometry)
        self.trips_destinations.crs = "epsg:4326"
        self.trips_destinations = self.trips_destinations.to_crs("epsg:3857")
        #print(self.trips_destinations.geometry)

        return self.trips_origins, self.trips_destinations

    def read_trips (self):

        path = os.path.join(
            self.norm_data_path,
            "od_trips",
            "bookings_.pickle"
        )
        self.bookings = pd.read_pickle(path)

        # self.bookings["euclidean_distance"] = self.bookings.euclidean_distance * 1000
        # self.bookings["driving_distance"] = self.bookings.driving_distance * 1000
        # self.bookings.duration = self.bookings.duration * 60

        return self.bookings
