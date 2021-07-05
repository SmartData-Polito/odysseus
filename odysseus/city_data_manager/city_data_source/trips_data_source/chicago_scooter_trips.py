import os

import pandas as pd
import numpy as np

from odysseus.city_data_manager.city_data_source.trips_data_source.trips_data_source import TripsDataSource


class ChicagoScooterTrips(TripsDataSource):

    def __init__(self):
        super().__init__("Chicago", "city_of_chicago", "e-scooter")

    def load_raw(self):

        raw_trips_data_path = os.path.join(
            self.raw_data_path,
            "E-Scooter_Trips_-_2019_Pilot.csv"
        )

        self.trips_df = pd.read_csv(raw_trips_data_path,
                                    dtype={
                                        "Start Community Area Name": np.str,
                                        "End Community Area Name": np.str,
                                        "Start Centroid Location": object,
                                        "End Centroid Location": object
                                    },
                                    parse_dates=[
                                        "Start Time",
                                        "End Time"
                                    ])

        return self.trips_df

    def normalise(self, year, month):

        self.trips_df_norm = self.trips_df
        self.trips_df_norm = self.trips_df_norm.rename({
            "Trip ID": "trip_id",
            "Start Time": "start_time",
            "End Time": "end_time",
            "Trip Distance": "driving_distance",
            "Trip Duration": "duration",
            "Accuracy": "accuracy",
            "Start Census Tract": "start_census_tract",
            "End Census Tract": "end_census_tract",
            "Start Community Area Number": "start_community_area_number",
            "End Community Area Number": "end_community_area_number",
            "Start Community Area Name": "start_community_area_name",
            "End Community Area Name": "end_community_area_name",
            "Start Centroid Latitude": "start_centroid_latitude",
            "Start Centroid Longitude": "start_centroid_longitude",
            "Start Centroid Location": "start_centroid_location",
            "End Centroid Latitude": "end_centroid_latitude",
            "End Centroid Longitude": "end_centroid_longitude",
            "End Centroid Location": "end_centroid_location"
        }, axis=1)

        self.trips_df_norm = super().normalise()

        self.trips_df_norm = self.trips_df_norm[
            (self.trips_df_norm.year == year) & (self.trips_df_norm.month == month)
        ]

        self.trips_df_norm.dropna(inplace=True, subset=[
            "trip_id",
            "start_time",
            "end_time",
            "driving_distance",
            "duration",
            "start_community_area_number",
            "end_community_area_number"
        ])

        self.save_norm()

        return self.trips_df_norm
