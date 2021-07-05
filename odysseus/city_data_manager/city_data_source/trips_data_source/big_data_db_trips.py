import os
import datetime

import pandas as pd

from odysseus.city_data_manager.city_data_source.trips_data_source.trips_data_source import TripsDataSource


class BigDataDBTrips(TripsDataSource):

    def __init__(self, city_name):
        super().__init__(city_name, "big_data_db", "car_sharing")

    def load_raw(self):

        raw_trips_data_path = os.path.join(
            self.raw_data_path,
            "Dataset_" + self.city_name + ".csv"
        )
        self.trips_df = pd.read_csv(raw_trips_data_path)
        return self.trips_df

    def normalise(self, year, month):

        self.trips_df_norm = self.trips_df
        self.trips_df_norm = self.trips_df_norm.rename({
            col: col.replace("init", "start").replace("final", "end").replace(
                "lon", "longitude"
            ).replace("_lat", "_latitude").replace("distance", "euclidean_distance")
            for col in self.trips_df_norm
        }, axis=1)

        self.trips_df_norm = self.trips_df_norm[[
            "plate",
            "start_time",
            "end_time",
            "start_longitude",
            "start_latitude",
            "end_longitude",
            "end_latitude",
            "euclidean_distance"
        ]]

        self.trips_df_norm.start_time = self.trips_df_norm.start_time.apply(
            lambda ts: datetime.datetime.fromtimestamp(ts)
        )
        self.trips_df_norm.end_time = self.trips_df_norm.end_time.apply(
            lambda ts: datetime.datetime.fromtimestamp(ts)
        )

        self.trips_df_norm.start_time = self.trips_df_norm.start_time - datetime.timedelta(hours=2)
        self.trips_df_norm.end_time = self.trips_df_norm.end_time - datetime.timedelta(hours=2)
        self.trips_df_norm.start_time = pd.to_datetime(self.trips_df_norm.start_time, utc=True)
        self.trips_df_norm.end_time = pd.to_datetime(self.trips_df_norm.end_time, utc=True)
        self.trips_df_norm.start_time = self.trips_df_norm.start_time.dt.tz_convert(self.tz)
        self.trips_df_norm.end_time = self.trips_df_norm.end_time.dt.tz_convert(self.tz)

        if month == 12:
            self.trips_df_norm = self.trips_df_norm[
                (self.trips_df_norm.start_time > datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc)) & (
                    self.trips_df_norm.start_time < datetime.datetime(year + 1, 1, 1, tzinfo=datetime.timezone.utc)
                )
            ]
        else:
            self.trips_df_norm = self.trips_df_norm[
                (self.trips_df_norm.start_time > datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc)) & (
                    self.trips_df_norm.start_time < datetime.datetime(year, month + 1, 1, tzinfo=datetime.timezone.utc)
                )
            ]

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
