import os
import datetime

import pandas as pd
from odysseus.utils.geospatial_utils import haversine

from odysseus.city_data_manager.city_data_source.trips_data_source.trips_data_source import TripsDataSource


class NewYorkCityBikeTrips(TripsDataSource):

    def __init__(self, city_name):
        super().__init__(city_name, 'citi_bike', 'bike')
        self.max_lon = -73.90
        self.min_lon = -74.04
        self.max_lat = 40.76
        self.min_lat = 40.66

    def load_raw(self, year, month):

        raw_trips_data_path = os.path.join(
            self.raw_data_path,
            '%s%s' % (str(year), str(month).zfill(2)) + "-citibike-tripdata.csv"
        )
        self.trips_df = pd.read_csv(raw_trips_data_path)
        return self.trips_df

    def normalise(self, year, month):

        self.trips_df_norm = self.trips_df

        new_columns = {}
        for column in self.trips_df_norm.columns:
            new_columns[column] = column.lower().replace(' ', '').strip().replace('station', '_station_')
        self.trips_df_norm = self.trips_df_norm.rename(columns=new_columns)

        self.trips_df_norm['count'] = 0
        self.trips_df_norm['tripduration'] = self.trips_df_norm['tripduration']

        self.trips_df_norm = self.trips_df_norm[
            (self.trips_df_norm['start_station_latitude'] >= self.min_lat) & (
                    self.trips_df_norm['start_station_latitude'] <= self.max_lat
            )
        ]
        self.trips_df_norm = self.trips_df_norm[
            (self.trips_df_norm['start_station_longitude'] >= self.min_lon) & (
                    self.trips_df_norm['start_station_longitude'] <= self.max_lon
            )
        ]
        self.trips_df_norm = self.trips_df_norm[
            (self.trips_df_norm['end_station_latitude'] >= self.min_lat) & (
                    self.trips_df_norm['end_station_latitude'] <= self.max_lat
            )
        ]
        self.trips_df_norm = self.trips_df_norm[
            (self.trips_df_norm['end_station_longitude'] >= self.min_lon) & (
                    self.trips_df_norm['end_station_longitude'] <= self.max_lon
            )
        ]

        self.trips_df_norm['distance'] = self.trips_df_norm.apply(
            lambda x: haversine(
                x.start_station_latitude,
                x.start_station_longitude,
                x.end_station_latitude,
                x.end_station_longitude
            ), axis=1
        )

        self.trips_df_norm['starttime'] = pd.to_datetime(self.trips_df_norm['starttime'])
        self.trips_df_norm['stoptime'] = pd.to_datetime(self.trips_df_norm['stoptime'])

        self.trips_df_norm = self.trips_df_norm.rename({
            "starttime": "start_time",
            "stoptime": "end_time",
            "tripduration": "duration",
            "distance": "driving_distance",
            "start_station_latitude": "start_latitude",
            "start_station_longitude": "start_longitude",
            "end_station_latitude": "end_latitude",
            "end_station_longitude": "end_longitude",
            "bikeid": "vehicle_id"

        }, axis=1)

        self.trips_df_norm["start_time"] = self.trips_df_norm["start_time"].sort_values()\
            .dt.tz_localize('US/Eastern', ambiguous="NaT").fillna(method="ffill")
        self.trips_df_norm["end_time"] = self.trips_df_norm["end_time"].sort_values()\
            .dt.tz_localize('US/Eastern', ambiguous="NaT").fillna(method="ffill")

        self.trips_df_norm = self.trips_df_norm.drop(
            [
                "start_station_id", "start_station_name", "end_station_id", "end_station_name",
                "usertype", "birthyear", "gender", "count"
            ],
            axis=1
        )

        self.trips_df_norm = super().normalise()

        self.trips_df_norm = self.trips_df_norm[
            (self.trips_df_norm.year == year) & (self.trips_df_norm.month == month)
        ]

        self.trips_df_norm.dropna(inplace=True)

        self.trips_df_norm.driving_distance = self.trips_df_norm.driving_distance * 1.609

        self.save_norm()

        return self.trips_df_norm
