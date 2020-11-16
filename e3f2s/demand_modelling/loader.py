import pytz
import geopandas as gpd
import pandas as pd
import shapely

from e3f2s.city_data_manager.config.config import *


class Loader:
    
    def __init__(self, city, data_source_id, year, month):
        
        self.city = city
        self.year = year
        self.month = month
        self.data_source_id = data_source_id

        self.trips = None
        self.trips_destinations = None
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

        if self.city == "Torino":
            self.tz = pytz.timezone("Europe/Rome")
        elif self.city == "Berlin":
            self.tz = pytz.timezone("Europe/Berlin")
        elif self.city == "Vancouver":
            self.tz = pytz.timezone("Europe/Berlin")
        elif self.city == "New_York_City":
            self.tz = pytz.timezone("America/New_York")
        elif self.city == "Minneapolis":
            self.tz = pytz.timezone("America/Chicago")
        elif self.city == "Louisville":
            self.tz = pytz.timezone("America/Kentucky/Louisville")
        elif self.city == "Austin" or self.city == "Kansas City":
            self.tz = pytz.timezone("US/Central")
        elif self.city == "Norfolk":
            self.tz = pytz.timezone("US/Eastern")

    def read_data (self):

        path = os.path.join(
            self.trips_data_path,
            "trips.pickle"
        )
        self.trips = gpd.GeoDataFrame(pd.read_pickle(path))

        path = os.path.join(
            self.points_data_path,
            "origins.pickle"
        )
        self.trips_origins = gpd.GeoDataFrame(pd.read_pickle(path))

        path = os.path.join(
            self.points_data_path,
            "destinations.pickle"
        )
        self.trips_destinations = gpd.GeoDataFrame(pd.read_pickle(path))

        self.trips_origins.crs = "epsg:4326"
        self.trips_destinations.crs = "epsg:4326"
        self.trips_origins["start_longitude"] = self.trips_origins.geometry.apply(lambda p: p.x)
        self.trips_origins["start_latitude"] = self.trips_origins.geometry.apply(lambda p: p.y)
        self.trips_destinations["end_longitude"] = self.trips_destinations.geometry.apply(lambda p: p.x)
        self.trips_destinations["end_latitude"] = self.trips_destinations.geometry.apply(lambda p: p.y)

        if self.city == 'Vancouver':
            self.trips = self.trips[self.trips.start_longitude < -122.9]
            self.trips = self.trips[self.trips.end_longitude < 0]
        elif self.city == 'Berlin':
            self.trips = self.trips[(self.trips.start_latitude > 51) & (self.trips.start_latitude < 53)]
            self.trips = self.trips[(self.trips.start_longitude > 12) & (self.trips.start_longitude < 14)]
            self.trips = self.trips[(self.trips.end_latitude > 51) & (self.trips.end_latitude < 53)]
            self.trips = self.trips[(self.trips.end_longitude > 12) & (self.trips.end_longitude < 14)]

        self.trips_origins = self.trips_origins.loc[self.trips.index]
        self.trips_destinations = self.trips_destinations.loc[self.trips.index]

        self.trips.start_time = pd.to_datetime(self.trips.start_time, utc=True)
        self.trips_origins.start_time = self.trips.start_time
        self.trips.end_time = pd.to_datetime(self.trips.end_time, utc=True)
        self.trips_destinations.end_time = self.trips.end_time

        return self.trips, self.trips_origins, self.trips_destinations
