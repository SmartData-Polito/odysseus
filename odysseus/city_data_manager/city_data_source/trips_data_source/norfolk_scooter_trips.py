import os

import pandas as pd
import numpy as np

from odysseus.city_data_manager.city_data_source.trips_data_source.trips_data_source import TripsDataSource
from odysseus.utils.geospatial_utils import miles_to_meters


class NorfolkScooterTrips(TripsDataSource):

    def __init__(self):
        super().__init__("Norfolk", "city_of_norfolk", "e-scooter")

    def load_raw(self):

        raw_trips_data_path = os.path.join(
            self.raw_data_path,
            "Scooters.csv"
        )

        self.trips_df = pd.read_csv(raw_trips_data_path,
                                    parse_dates=[
                                        "Starting Date",
                                        "Ending Date"
                                    ])

        return self.trips_df

    def normalise(self, year, month):

        self.trips_df_norm = self.trips_df
        self.trips_df_norm = self.trips_df_norm.rename({
            "Starting Tract": "start_census_tract",
            "Ending Tract": "end_census_tract",
            "Trip Duration (min)": "duration",
            "Trip Distance (miles)": "driving_distance",
            "Starting Date": "start_time",
            "Starting Hour": "start_hour",
            "Ending Date": "end_time",
            "Ending Hour": "end_hour"
        }, axis=1)

        self.trips_df_norm.dropna(inplace=True)

        self.trips_df_norm.start_census_tract = self.trips_df_norm.start_census_tract.astype(int)
        self.trips_df_norm.end_census_tract = self.trips_df_norm.end_census_tract.astype(int)

        self.trips_df_norm.driving_distance = self.trips_df_norm.driving_distance.apply(miles_to_meters)

        self.trips_df_norm = super().normalise()

        self.trips_df_norm = self.trips_df_norm[
            (self.trips_df_norm.year == year) & (self.trips_df_norm.month == month)
        ]

        self.save_norm()

        return self.trips_df_norm
