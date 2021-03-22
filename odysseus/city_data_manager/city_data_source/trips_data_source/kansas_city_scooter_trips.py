import os

import pandas as pd

from odysseus.city_data_manager.city_data_source.trips_data_source.trips_data_source import TripsDataSource
from odysseus.utils.geospatial_utils import miles_to_meters


class KansasCityScooterTrips(TripsDataSource):

    def __init__(self):
        super().__init__("Kansas City", "city_of_kansas_city", "e-scooter")

    def load_raw(self):

        raw_trips_data_path = os.path.join(
            self.raw_data_path,
            "Microtransit__Scooter_and_Ebike__Trips.csv"
        )

        self.trips_df = pd.read_csv(raw_trips_data_path,
                                    parse_dates=[
                                        ["Start Date", "Start Time"],
                                        ["End Date", "End Time"]
                                    ])
        return self.trips_df

    def normalise(self, year, month):

        self.trips_df_norm = self.trips_df
        self.trips_df_norm = self.trips_df_norm.rename({
            "Start Date_Start Time": "start_time",
            "End Date_End Time": "end_time",
            "Trip Duration": "duration",
            "Trip Distance": "driving_distance",
            "Start Latitude": "start_latitude",
            "Start Longitude": "start_longitude",
            "End Latitude": "end_latitude",
            "End Longitude": "end_longitude",
        }, axis=1)

        self.trips_df_norm["start_time"] = self.trips_df_norm["start_time"]\
            .dt.tz_localize('utc').dt.tz_convert('US/Central')
        self.trips_df_norm["end_time"] = self.trips_df_norm["end_time"]\
            .dt.tz_localize('utc').dt.tz_convert('US/Central')

        self.trips_df_norm = self.trips_df_norm.drop(["Start Location", "End Location", "hour", "Day of Week"], axis=1)

        self.trips_df_norm = super().normalise()

        self.trips_df_norm = self.trips_df_norm[
            (self.trips_df_norm.year == year) & (self.trips_df_norm.month == month)
        ]

        self.trips_df_norm.dropna(inplace=True)

        self.trips_df_norm.driving_distance = self.trips_df_norm.driving_distance.apply(miles_to_meters)

        self.save_norm()

        return self.trips_df_norm
