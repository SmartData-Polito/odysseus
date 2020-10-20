import os
import geopandas as gpd
import pandas as pd
import shapely

from e3f2s.city_data_manager.config.config import *


class Loader:
    
    def __init__(self, city, data_source_id, year, month, bin_side_length):
        
        self.city = city
        self.year = year
        self.month = month
        self.data_source_id = data_source_id

        self.trips = None
        self.trips_destination = None
        self.trips_origins = None

        self.points_data_path = os.path.join(
            data_paths_dict[self.city]["od_trips"]["points"],
            data_source_id,
            "_".join([str(year), str(month)])
        )
        self.trips_data_path = os.path.join(
            data_paths_dict[self.city]["od_trips"]["trips"],
            data_source_id,
            "_".join([str(year), str(month)])
        )

    def read_origins_destinations (self):

        path = os.path.join(
            self.points_data_path,
            "origins.pickle"
        )
        self.trips_origins = pd.read_pickle(path)
        self.trips_origins["start_longitude"] = self.trips_origins.geometry.apply(lambda p: p.x)
        self.trips_origins["start_latitude"] = self.trips_origins.geometry.apply(lambda p: p.y)

        path = os.path.join(
            self.points_data_path,
            "destinations.pickle"
        )
        self.trips_destinations = pd.read_pickle(path)
        self.trips_destinations["end_longitude"] = self.trips_destinations.geometry.apply(lambda p: p.x)
        self.trips_destinations["end_latitude"] = self.trips_destinations.geometry.apply(lambda p: p.y)

        self.trips_origins = self.bookings.copy()
        self.trips_destinations = self.bookings.copy()

        self.trips_origins["geometry"] = self.trips_origins.apply(
            lambda row: shapely.geometry.Point(row["start_longitude"], row["start_latitude"]), axis=1
        )
        self.trips_destinations["geometry"] = self.trips_destinations.apply(
            lambda row: shapely.geometry.Point(row["end_longitude"], row["end_latitude"]), axis=1
        )
        self.trips_origins = gpd.GeoDataFrame(self.trips_origins)
        self.trips_destinations = gpd.GeoDataFrame(self.trips_destinations)

        self.trips_origins.crs = "epsg:4326"
        self.trips_origins = self.trips_origins.to_crs("epsg:3857")
        self.trips_destinations.crs = "epsg:4326"
        self.trips_destinations = self.trips_destinations.to_crs("epsg:3857")

        return self.trips_origins, self.trips_destinations

    def read_trips (self):

        path = os.path.join(
            self.trips_data_path,
            "trips.pickle"
        )
        self.bookings = pd.read_pickle(path)
        return self.bookings
