import os
import datetime

import pandas as pd

from odysseus.city_data_manager.geo_trips.trips_data_source import TripsDataSource


class CustomTrips(TripsDataSource):

    def __init__(self, city_name):
        super().__init__(city_name, "custom_trips")

    def load_raw(self):

        raw_trips_data_path = os.path.join(
            self.raw_data_path,
            "custom_trips.csv"
        )
        self.trips_df = pd.read_csv(raw_trips_data_path)
        return self.trips_df

    def normalise(self, year, month):

        self.trips_df_norm = self.trips_df

        self.trips_df_norm = self.trips_df_norm[[
            "start_time",
            "end_time",
            "start_longitude",
            "start_latitude",
            "end_longitude",
            "end_latitude",
        ]]

        self.trips_df_norm.start_time = pd.to_datetime(self.trips_df_norm.start_time)
        self.trips_df_norm.end_time = pd.to_datetime(self.trips_df_norm.end_time)

        self.trips_df_norm = super().normalise()
        self.save_norm(year, month)

        return self.trips_df_norm

    def save_norm(self, year, month):

        print(self.trips_df_norm.shape)

        trips_df_norm_year_month = self.trips_df_norm[
            (self.trips_df_norm.start_year == year) & (self.trips_df_norm.start_month == month)
        ]

        print(trips_df_norm_year_month.shape)

        if len(trips_df_norm_year_month):
            trips_df_norm_year_month.to_csv(
                os.path.join(
                    self.norm_data_path,
                    "_".join([str(year), str(month)]) + ".csv"
                )
            )
            trips_df_norm_year_month.to_pickle(
                os.path.join(
                    self.norm_data_path,
                    "_".join([str(year), str(month)]) + ".pickle"
                )
            )
