import os

import pandas as pd
import numpy as np

from odysseus.city_data_manager.city_data_source.trips_data_source.trips_data_source import TripsDataSource


class LouisvilleScooterTrips(TripsDataSource):

    def __init__(self):
        super().__init__("Louisville", "city_of_louisville", "e-scooter")

    def load_raw(self):

        raw_trips_data_paths = [
            os.path.join(
                self.raw_data_path,
                "DocklessTripOpenData_10.csv"
            ),
            os.path.join(
                self.raw_data_path,
                "Louisville-Dockless-Trips .csv"
            )]

        trips_dfs = [pd.read_csv(raw_trips_data_path) for raw_trips_data_path in raw_trips_data_paths]

        self.trips_df = pd.concat(trips_dfs, axis=0, ignore_index=True)

        def filter_quantiles(x, lower, upper):
            return x[x.between(x.quantile(lower), x.quantile(upper))]

        self.trips_df.StartLatitude = filter_quantiles(self.trips_df.StartLatitude, 0.01, 0.99)
        self.trips_df.StartLongitude = filter_quantiles(self.trips_df.StartLongitude, 0.01, 0.99)
        self.trips_df.EndLatitude = filter_quantiles(self.trips_df.EndLatitude, 0.01, 0.99)
        self.trips_df.EndLongitude = filter_quantiles(self.trips_df.EndLongitude, 0.01, 0.99)

        return self.trips_df

    def normalise(self, year, month):

        self.trips_df_norm = self.trips_df
        self.trips_df_norm = self.trips_df_norm.rename({
            "TripDuration": "duration",
            "TripDistance": "driving_distance",
            "StartDate": "start_date",
            "EndDate": "end_date",
            "StartTime": "start_time",
            "EndTime": "end_time",
            "StartLatitude": "start_latitude",
            "StartLongitude": "start_longitude",
            "EndLatitude": "end_latitude",
            "EndLongitude": "end_longitude",

        }, axis=1).replace("nan", np.NaN).dropna()
        self.trips_df_norm.start_time = self.trips_df_norm.start_time.astype(str).apply(
            lambda string: string.replace("24", "0")
        )
        self.trips_df_norm.end_time = self.trips_df_norm.end_time.astype(str).apply(
            lambda string: string.replace("24", "0")
        )
        self.trips_df_norm.start_time = pd.to_datetime(
            self.trips_df_norm.start_date + " " + self.trips_df_norm.start_time
        )
        self.trips_df_norm.end_time = pd.to_datetime(
            self.trips_df_norm.end_date + " " + self.trips_df_norm.end_time
        )
        self.trips_df_norm.start_time = pd.to_datetime(
            self.trips_df_norm.start_time
        ).apply(lambda x: pd.Timestamp(x, tz="America/Kentucky/Louisville"))
        self.trips_df_norm.end_time = pd.to_datetime(
            self.trips_df_norm.end_time
        ).apply(lambda x: pd.Timestamp(x, tz="America/Kentucky/Louisville"))

        self.trips_df_norm.driving_distance *= 1609
        self.trips_df_norm.duration *= 60
        self.trips_df_norm = self.trips_df_norm[[
            "start_time",
            "end_time",
            "duration",
            "start_latitude",
            "start_longitude",
            "end_latitude",
            "end_longitude",
            "driving_distance",
        ]]

        self.trips_df_norm = super().normalise()
        self.trips_df_norm = self.trips_df_norm[
            (self.trips_df_norm.year == year) & (self.trips_df_norm.month == month)
        ]
        self.save_norm()

        return self.trips_df_norm
