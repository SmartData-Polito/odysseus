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

    def read_data (self):

        path = os.path.join(
            self.trips_data_path,
            "trips.pickle"
        )
        self.bookings = pd.read_pickle(path)

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

        # print(
        #     self.bookings[[
        #         'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude'
        #     ]].describe()
        # )

        if self.city == 'Vancouver':
            self.bookings = self.bookings[self.bookings.start_longitude < 0]
            self.bookings = self.bookings[self.bookings.end_longitude < 0]
        elif self.city == 'Berlin':
            self.bookings = self.bookings[(self.bookings.start_latitude > 51) & (self.bookings.start_latitude < 53)]
            self.bookings = self.bookings[(self.bookings.start_longitude > 12) & (self.bookings.start_longitude < 14)]
            self.bookings = self.bookings[(self.bookings.end_latitude > 51) & (self.bookings.end_latitude < 53)]
            self.bookings = self.bookings[(self.bookings.end_longitude > 12) & (self.bookings.end_longitude < 14)]

        self.trips_origins = self.trips_origins.loc[self.bookings.index]
        self.trips_destinations = self.trips_destinations.loc[self.bookings.index]

        # print(
        #     self.bookings[[
        #         'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude'
        #     ]].describe()
        # )

        print(
            self.bookings[[
                'start_time', 'end_time'
            ]].dtypes
        )

        print(pd.to_datetime(self.bookings.start_time))

        self.bookings.start_time = pd.to_datetime(self.bookings.start_time, utc=True)
        self.trips_origins.start_time = self.bookings.start_time
        self.bookings.end_time = pd.to_datetime(self.bookings.end_time, utc=True)
        self.trips_destinations.end_time = self.bookings.end_time

        print(
            self.bookings[[
                'start_time', 'end_time'
            ]].dtypes
        )

        return self.bookings, self.trips_origins, self.trips_destinations
