import os

import pandas as pd

from odysseus.city_data_manager.city_data_source.trips_data_source.trips_data_source import TripsDataSource


class CalgaryScooterTrips(TripsDataSource):

    def __init__(self):
        super().__init__("Calgary", "city_of_calgary", "e-scooter")

    def load_raw(self):
        raw_trips_data_path = os.path.join(
            self.raw_data_path,
            "Shared_Mobility_Pilot_Trips.csv"
        )

        self.trips_df = pd.read_csv(raw_trips_data_path,
                                    parse_dates=[
                                        "start_date"
                                    ])
        return self.trips_df

    def normalise(self, year, month):
        self.trips_df_norm = self.trips_df
        self.trips_df_norm = self.trips_df_norm.rename({
            "trip_distance": "driving_distance",
            "trip_duration": "duration"
        }, axis=1)

        self.trips_df_norm = self.trips_df_norm[self.trips_df_norm.vehicle_type == "scooter"]

        self.trips_df_norm = self.trips_df_norm[[
            "start_date",
            "start_hour",
            "driving_distance",
            "duration",
            "starting_grid_id",
            "ending_grid_id"
        ]]

        self.trips_df_norm["start_time"] = self.trips_df_norm.apply(
            lambda row: pd.Timestamp(
                year=row.start_date.year,
                month=row.start_date.month,
                day=row.start_date.day,
                hour=row.start_hour
            ),
            axis=1
        )

        self.trips_df_norm["end_time"] = \
            self.trips_df_norm["start_time"] + pd.to_timedelta(self.trips_df_norm["duration"], unit='s')

        self.trips_df_norm = super().normalise()

        self.trips_df_norm = self.trips_df_norm[
            (self.trips_df_norm.year == year) & (self.trips_df_norm.month == month)
            ]

        self.trips_df_norm.dropna(inplace=True)

        self.save_norm()

        return self.trips_df_norm
