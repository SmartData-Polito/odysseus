import pytz
import geopandas as gpd
import pandas as pd
import shapely

from odysseus.city_data_manager.config.config import *


class Loader:
    
    def __init__(self, city, data_source_id, year, month):
        
        self.city_name = city
        self.year = year
        self.month = month
        self.data_source_id = data_source_id

        self.trips = None
        self.trips_destinations = None
        self.trips_origins = None

        self.points_data_path = os.path.join(
            data_paths_dict[self.city_name]["od_trips"]["points"],
            data_source_id,
            "_".join([str(year), str(month)])
        )
        self.trips_data_path = os.path.join(
            data_paths_dict[self.city_name]["od_trips"]["trips"],
            data_source_id,
            "_".join([str(year), str(month)])
        )

        if self.city_name == "Roma" or self.city_name == "Torino" or self.city_name == "Milano":
            self.tz = pytz.timezone("Europe/Rome")
        elif self.city_name == "Amsterdam":
            self.tz = pytz.timezone("Europe/Amsterdam")
        elif self.city_name == "Madrid":
            self.tz = pytz.timezone("Europe/Madrid")
        elif self.city_name == "Berlin":
            self.tz = pytz.timezone("Europe/Berlin")
        elif self.city_name == "New_York_City":
            self.tz = pytz.timezone("America/New_York")
        elif self.city_name == "Vancouver":
            self.tz = pytz.timezone("America/Vancouver")
        elif self.city_name == "Louisville":
            self.tz = pytz.timezone("America/Kentucky/Louisville")
        elif self.city_name == "Minneapolis" or self.city_name == "Chicago":
            self.tz = pytz.timezone("America/Chicago")
        elif self.city_name == "Austin" or self.city_name == "Kansas City":
            self.tz = pytz.timezone("US/Central")
        elif self.city_name == "Norfolk":
            self.tz = pytz.timezone("US/Eastern")
        elif self.city_name == "Calgary":
            self.tz = pytz.timezone("Canada/Mountain")

    def read_data (self):

        path = os.path.join(
            self.trips_data_path,
            "trips.pickle"
        )
        self.trips = gpd.GeoDataFrame(pd.read_pickle(path))
        print(self.trips.shape)
        path = os.path.join(
            self.points_data_path,
            "origins.pickle"
        )
        self.trips_origins = gpd.GeoDataFrame(pd.read_pickle(path))
        print(self.trips_origins.shape)

        path = os.path.join(
            self.points_data_path,
            "destinations.pickle"
        )
        self.trips_destinations = gpd.GeoDataFrame(pd.read_pickle(path))
        print(self.trips_destinations.shape)

        self.trips_origins.crs = "epsg:4326"
        self.trips_destinations.crs = "epsg:4326"
        self.trips_origins["start_longitude"] = self.trips_origins.geometry.apply(lambda p: p.x)
        self.trips_origins["start_latitude"] = self.trips_origins.geometry.apply(lambda p: p.y)
        self.trips_destinations["end_longitude"] = self.trips_destinations.geometry.apply(lambda p: p.x)
        self.trips_destinations["end_latitude"] = self.trips_destinations.geometry.apply(lambda p: p.y)

        if self.city_name == 'Vancouver':
            self.trips = self.trips[self.trips.start_longitude < -122.9]
            self.trips = self.trips[self.trips.end_longitude < 0]
        elif self.city_name == 'Berlin':
            self.trips = self.trips[(self.trips.start_latitude > 51) & (self.trips.start_latitude < 53)]
            self.trips = self.trips[(self.trips.start_longitude > 12) & (self.trips.start_longitude < 14)]
            self.trips = self.trips[(self.trips.end_latitude > 51) & (self.trips.end_latitude < 53)]
            self.trips = self.trips[(self.trips.end_longitude > 12) & (self.trips.end_longitude < 14)]
        elif self.city_name == 'Minneapolis':
            self.trips = self.trips[(self.trips.start_latitude > 44.88) & (self.trips.start_latitude < 45.06)]
            self.trips = self.trips[(self.trips.start_longitude > -93.35) & (self.trips.start_longitude < -93.20)]
            self.trips = self.trips[(self.trips.end_latitude > 44.88) & (self.trips.end_latitude < 45.06)]
            self.trips = self.trips[(self.trips.end_longitude > -93.35) & (self.trips.end_longitude < -93.20)]
        elif self.city_name == 'Austin':
            self.trips = self.trips[(self.trips.start_latitude > 30.15) & (self.trips.start_latitude < 30.40)]
            self.trips = self.trips[(self.trips.start_longitude > -97.85) & (self.trips.start_longitude < -97.65)]
            self.trips = self.trips[(self.trips.end_latitude > 30.15) & (self.trips.end_latitude < 30.40)]
            self.trips = self.trips[(self.trips.end_longitude > -97.85) & (self.trips.end_longitude < -97.65)]
        elif self.city_name == 'Norfolk':
            self.trips = self.trips[(self.trips.start_latitude > 36.775) & (self.trips.start_latitude < 36.975)]
            self.trips = self.trips[(self.trips.start_longitude > -76.35) & (self.trips.start_longitude < -76.15)]
            self.trips = self.trips[(self.trips.end_latitude > 36.775) & (self.trips.end_latitude < 36.975)]
            self.trips = self.trips[(self.trips.end_longitude > -76.35) & (self.trips.end_longitude < -76.15)]
        elif self.city_name == 'Kansas City':
            self.trips = self.trips[(self.trips.start_latitude > 38.950) & (self.trips.start_latitude < 39.150)]
            self.trips = self.trips[(self.trips.start_longitude > -94.675) & (self.trips.start_longitude < -94.45)]
            self.trips = self.trips[(self.trips.end_latitude > 38.950) & (self.trips.end_latitude < 39.150)]
            self.trips = self.trips[(self.trips.end_longitude > -94.675) & (self.trips.end_longitude < -94.45)]
        elif self.city_name == 'Chicago':
            self.trips = self.trips[(self.trips.start_latitude > 41.80) & (self.trips.start_latitude < 41.98)]
            self.trips = self.trips[(self.trips.start_longitude > -87.85) & (self.trips.start_longitude < -87.60)]
            self.trips = self.trips[(self.trips.end_latitude > 41.80) & (self.trips.end_latitude < 41.98)]
            self.trips = self.trips[(self.trips.end_longitude > -87.85) & (self.trips.end_longitude < -87.60)]
        elif self.city_name == 'Calgary':
            self.trips = self.trips[(self.trips.start_latitude > 50.95) & (self.trips.start_latitude < 51.10)]
            self.trips = self.trips[(self.trips.start_longitude > -114.25) & (self.trips.start_longitude < -113.95)]
            self.trips = self.trips[(self.trips.end_latitude > 50.95) & (self.trips.end_latitude < 51.10)]
            self.trips = self.trips[(self.trips.end_longitude > -114.25) & (self.trips.end_longitude < -113.95)]

        if "trip_id" in self.trips.columns:
            self.trips_origins = gpd.GeoDataFrame(pd.merge(
                self.trips_origins,
                self.trips["trip_id"],
            ))
            self.trips_origins.crs = "epsg:4326"
            self.trips_destinations = gpd.GeoDataFrame(pd.merge(
                self.trips_destinations,
                self.trips["trip_id"],
            ))
            self.trips_destinations.crs = "epsg:4326"
        else:
            self.trips_origins = self.trips_origins.loc[self.trips.index]
            self.trips_destinations = self.trips_destinations.loc[self.trips.index]

        self.trips.start_time = pd.to_datetime(self.trips.start_time)
        self.trips_origins.start_time = self.trips.start_time
        self.trips.end_time = pd.to_datetime(self.trips.end_time)
        self.trips_destinations.end_time = self.trips.end_time

        return self.trips, self.trips_origins, self.trips_destinations
