import os
import datetime

import pandas as pd

from e3f2s.city_data_manager.city_data_source.trips_data_source.trips_data_source import TripsDataSource


class NewYorkCityBikeTrips(TripsDataSource):

    def __init__(self, city_name):
        super().__init__(city_name, 'city_of_new_york_city', 'bike')

    def load_raw(self):

        raw_trips_data_path = os.path.join(
            self.raw_data_path,
            "citibike-tripdata.csv"
        )
        self.trips_df = pd.read_csv(raw_trips_data_path)
        return self.trips_df

    def normalise(self, year, month):

        self.trips_df_norm = self.trips_df
        self.trips_df_norm = self.trips_df_norm.rename({
            "starttime": "start_time",
            "stoptime": "end_time",
            "tripduration": "duration",
            "distance": "driving_distance",
            "start_station_latitude": "start_latitude",
            "start_station_longitude": "start_longitude",
            "end_station_latitude": "end_latitude",
            "end_station_longitude": "end_longitude",
        }, axis=1)

        self.trips_df_norm["start_time"] = self.trips_df_norm["start_time"]\
            .dt.tz_localize('US/Eastern')
        self.trips_df_norm["end_time"] = self.trips_df_norm["end_time"]\
            .dt.tz_localize('US/Eastern')

        self.trips_df_norm = self.trips_df_norm.drop(
            [
                "start_station_id", "start_station_name", "end_station_id", "end_station_name",
                "bikeid","usertype","birthyear","gender","count"
            ],
            axis=1
        )

        self.trips_df_norm = super().normalise()

        self.trips_df_norm = self.trips_df_norm[
            (self.trips_df_norm.year == year) & (self.trips_df_norm.month == month)
        ]

        self.trips_df_norm.dropna(inplace=True)

        self.trips_df_norm.driving_distance = self.trips_df_norm.driving_distance.apply(miles_to_meters)

        self.save_norm()

        return self.trips_df_norm