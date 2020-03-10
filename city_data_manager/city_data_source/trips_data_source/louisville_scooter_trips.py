import os

import pandas as pd

from city_data_manager.city_data_source.trips_data_source.trips_data_source import TripsDataSource


class LouisvilleScooterTrips(TripsDataSource):

	def __init__(self):
		super().__init__("Louisville", "city_of_louisville", "e-scooter")

	def load_raw(self):

		raw_trips_data_path = os.path.join(
			self.raw_data_path,
			"DocklessTripOpenData_6.csv"
		)
		self.trips_df = pd.read_csv(raw_trips_data_path)
		return self.trips_df

	def normalise(self):

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

		}, axis=1)
		self.trips_df_norm.start_time = self.trips_df_norm.start_time.apply(
			lambda string: string.replace("24", "0")
		)
		self.trips_df_norm.end_time = self.trips_df_norm.end_time.apply(
			lambda string: string.replace("24", "0")
		)
		self.trips_df_norm.start_time = pd.to_datetime(
			self.trips_df_norm.start_date + " " + self.trips_df_norm.start_time
		)
		self.trips_df_norm.end_time = pd.to_datetime(
			self.trips_df_norm.end_date + " " + self.trips_df_norm.end_time
		)
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

		return self.trips_df_norm
