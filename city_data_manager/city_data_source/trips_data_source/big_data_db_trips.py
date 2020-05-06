import os
import datetime

import numpy as np
import pandas as pd

from city_data_manager.city_data_source.trips_data_source.trips_data_source import TripsDataSource


class BigDataDBTrips(TripsDataSource):

    def __init__(self, city):
        super().__init__(city, "big_data_db_polito", "car_sharing")

    def load_raw(self):

        raw_trips_data_path = os.path.join(
            self.raw_data_path,
            "Dataset_" + self.city_id + ".csv"
        )
        self.trips_df = pd.read_csv(raw_trips_data_path)

        return self.trips_df

    def normalise(self):

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
        self.trips_df_norm = super().normalise()

        return self.trips_df_norm
