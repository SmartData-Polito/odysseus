import os

import pandas as pd
import numpy as np

from e3f2s.city_data_manager.city_data_source.trips_data_source.trips_data_source import TripsDataSource


class AustinScooterTrips(TripsDataSource):

    def __init__(self):
        super().__init__("Austin", "city_of_austin", "e-scooter")

    def load_raw(self):

        raw_trips_data_path = os.path.join(
            self.raw_data_path,
            "Shared_Micromobility_Vehicle_Trips.csv"
        )

        self.trips_df = pd.read_csv(raw_trips_data_path,
                                    dtype={
                                        "Council District (Start)": np.float64,
                                        "Council District (End)": np.float64,
                                        "Census Tract Start": np.float64,
                                        "Census Tract End": np.float64
                                    },
                                    na_values={
                                        "Council District (Start)": "None",
                                        "Council District (End)": "None",
                                        "Census Tract Start": ["OUT_OF_BOUNDS", "None"],
                                        "Census Tract End": ["OUT_OF_BOUNDS", "None"]
                                    },
                                    parse_dates=[
                                        "Start Time",
                                        "End Time",
                                        "Modified Date"
                                    ])

        return self.trips_df

    def normalise(self, year, month):

        self.trips_df_norm = self.trips_df
        self.trips_df_norm = self.trips_df_norm.rename({
            "ID": "trip_id",
            "Device ID": "vehicle_id",
            "Vehicle Type": "vehicle_type",
            "Trip Duration": "duration",
            "Trip Distance": "driving_distance",
            "Start Time": "start_time",
            "End Time": "end_time",
            "Modified Date": "modified_date",
            "Month": "month",
            "Hour": "start_hour",
            "Day of Week": "start_weekday",
            "Council District (Start)": "start_council_district",
            "Council District (End)": "end_council_district",
            "Year": "year",
            "Census Tract Start": "start_census_tract",
            "Census Tract End": "end_census_tract"
        }, axis=1)

        self.trips_df_norm = self.trips_df_norm[self.trips_df_norm.vehicle_type == "scooter"]

        self.trips_df_norm = self.trips_df_norm[[
            "start_time",
            "end_time",
            "year",
            "month",
            "start_hour",
            "duration",
            "start_census_tract",
            "end_census_tract",
            "driving_distance"
        ]]

        self.trips_df_norm = self.trips_df_norm[
            (self.trips_df_norm.year == year) & (self.trips_df_norm.month == month)
            ]

        self.trips_df_norm.dropna(inplace=True)

        self.trips_df_norm.start_census_tract = self.trips_df_norm.start_census_tract\
            .astype(int)\
            .apply(lambda x: x - 48453000000)

        self.trips_df_norm.end_census_tract = self.trips_df_norm.end_census_tract\
            .astype(int)\
            .apply(lambda x: x - 48453000000)

        self.trips_df_norm = super().normalise()

        self.save_norm()

        return self.trips_df_norm
