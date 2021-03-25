import os

import pandas as pd

from odysseus.city_data_manager.city_data_source.trips_data_source.trips_data_source import TripsDataSource


class MinneapolisScooterTrips(TripsDataSource):

	def __init__(self):
		super().__init__("Minneapolis", "city_of_minneapolis", "e-scooter")

	def load_raw(self, year, month):

		year = str(year)
		months_dict = {
			5: "May",
			6: "June",
			7: "July",
			8: "August",
			9: "September",
			10: "October",
			11: "November"
		}
		month = months_dict[month]

		raw_trips_data_path = os.path.join(
			self.raw_data_path,
			"_".join(["Motorized", "Foot", "Scooter", "Trips", month, year]) + ".csv"
		)
		self.trips_df = pd.read_csv(raw_trips_data_path, parse_dates=["StartTime", "EndTime"])

		self.trips_df.StartTime = pd.to_datetime(self.trips_df.StartTime, utc=True, format="")
		self.trips_df.EndTime = pd.to_datetime(self.trips_df.EndTime, utc=True)


		return self.trips_df

	def normalise(self, year, month):

		self.trips_df_norm = self.trips_df
		self.trips_df_norm = self.trips_df_norm.rename({
			"TripId": "trip_id",
			"ObjectId": "object_id",
			"TripDuration": "duration",
			"TripDistance": "driving_distance",
			"StartTime": "start_time",
			"EndTime": "end_time",
			"StartCenterlineID": "start_centerline_id",
			"EndCenterlineID": "end_centerline_id",
		}, axis=1)
		self.trips_df_norm.start_time = pd.to_datetime(self.trips_df_norm.start_time, utc=True)
		self.trips_df_norm.end_time = pd.to_datetime(self.trips_df_norm.end_time, utc=True)
		self.trips_df_norm.start_time = self.trips_df_norm.start_time.dt.tz_convert('America/Chicago')
		self.trips_df_norm.end_time = self.trips_df_norm.end_time.dt.tz_convert('America/Chicago')
		self.trips_df_norm = self.trips_df_norm[[
			"start_time",
			"end_time",
			"duration",
			"start_centerline_id",
			"end_centerline_id",
			"driving_distance",
		]]
		self.trips_df_norm.start_centerline_id = self.trips_df_norm.start_centerline_id.astype(str)
		self.trips_df_norm.end_centerline_id = self.trips_df_norm.end_centerline_id.astype(str)
		self.trips_df_norm.dropna(inplace=True)
		self.trips_df_norm = super().normalise()
		self.trips_df_norm = self.trips_df_norm[
			(self.trips_df_norm.year == year) & (self.trips_df_norm.month == month)
		]
		self.save_norm()
		return self.trips_df_norm
