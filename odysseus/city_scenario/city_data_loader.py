import pytz
import geopandas as gpd
import pandas as pd
from odysseus.path_config.path_config import *
from odysseus.utils.time_utils import *
from odysseus.utils.geospatial_utils import get_haversine_distance


class CityDataLoader:
    
    def __init__(self, city_name, data_source_id):
        
        self.city_name = city_name
        self.data_source_id = data_source_id

        self.trips = pd.DataFrame()
        self.trips_destinations = pd.DataFrame()
        self.trips_origins = pd.DataFrame()

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

    def read_year_month_data (self, year, month):

        self.points_data_path = os.path.join(
            data_paths_dict[self.city_name]["od_trips"]["points"],
            self.data_source_id,
            "_".join([str(year), str(month)])
        )
        self.trips_data_path = os.path.join(
            data_paths_dict[self.city_name]["od_trips"]["trips"],
            self.data_source_id,
            "_".join([str(year), str(month)])
        )

        path = os.path.join(
            self.trips_data_path,
            "trips.pickle"
        )
        self.year_month_trips = gpd.GeoDataFrame(pd.read_pickle(path))
        path = os.path.join(
            self.points_data_path,
            "origins.pickle"
        )
        self.year_month_trips_origins = gpd.GeoDataFrame(pd.read_pickle(path))
        path = os.path.join(
            self.points_data_path,
            "destinations.pickle"
        )
        self.year_month_trips_destinations = gpd.GeoDataFrame(pd.read_pickle(path))

        self.year_month_trips_origins.crs = "epsg:4326"
        self.year_month_trips_destinations.crs = "epsg:4326"
        self.year_month_trips_origins["start_longitude"] = self.year_month_trips_origins.geometry.apply(lambda p: p.x)
        self.year_month_trips_origins["start_latitude"] = self.year_month_trips_origins.geometry.apply(lambda p: p.y)
        self.year_month_trips_destinations["end_longitude"] = self.year_month_trips_destinations.geometry.apply(lambda p: p.x)
        self.year_month_trips_destinations["end_latitude"] = self.year_month_trips_destinations.geometry.apply(lambda p: p.y)

        if "trip_id" in self.year_month_trips.columns:
            self.year_month_trips_origins = gpd.GeoDataFrame(pd.merge(
                self.year_month_trips_origins,
                self.year_month_trips["trip_id"],
            ))
            self.year_month_trips_origins.crs = "epsg:4326"
            self.year_month_trips_destinations = gpd.GeoDataFrame(pd.merge(
                self.year_month_trips_destinations,
                self.year_month_trips["trip_id"],
            ))
            self.year_month_trips_destinations.crs = "epsg:4326"
        else:
            self.year_month_trips_origins = self.year_month_trips_origins.loc[self.year_month_trips.index]
            self.year_month_trips_destinations = self.year_month_trips_destinations.loc[self.year_month_trips.index]

        self.year_month_trips.start_time = pd.to_datetime(self.year_month_trips.start_time)
        self.year_month_trips_origins.start_time = self.year_month_trips.start_time
        self.year_month_trips.end_time = pd.to_datetime(self.year_month_trips.end_time)
        self.year_month_trips_destinations.end_time = self.year_month_trips.end_time

        return self.year_month_trips, self.year_month_trips_origins, self.year_month_trips_destinations

    def read_year_month_range_data(self, start_month, start_year, end_month, end_year):

        self.trips = pd.DataFrame()
        self.trips_origins = pd.DataFrame()
        self.trips_destinations = pd.DataFrame()

        for year, month in month_year_iter(start_month, start_year, end_month, end_year):
            bookings, origins, destinations = self.read_year_month_data(year, month)
            self.trips = pd.concat([self.trips, bookings], ignore_index=True)
            self.trips_origins = pd.concat([
                self.trips_origins, origins
            ], ignore_index=True, sort=False)
            self.trips_destinations = pd.concat([
                self.trips_destinations, destinations
            ], ignore_index=True, sort=False)

        self.trips["date"] = self.trips.start_time.apply(lambda d: d.date())
        self.trips["daytype"] = self.trips.start_daytype
        self.trips["city"] = self.city_name
        self.trips["euclidean_distance"] = self.trips.apply(
            lambda pp: get_haversine_distance(pp["start_longitude"], pp["start_latitude"], pp["end_longitude"], pp["end_latitude"]),
            axis=1
        )

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

        return self.trips, self.trips_origins, self.trips_destinations
