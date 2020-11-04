import os
import pytz
import pandas as pd

from e3f2s.city_data_manager.config.config import *
from e3f2s.utils.path_utils import check_create_path
from e3f2s.utils.time_utils import get_time_group_columns


class TripsDataSource:

	def __init__(self, city_name, data_source_id, vehicles_type_id):

		self.city_name = city_name
		self.data_source_id = data_source_id
		self.vehicles_type_id = vehicles_type_id
		self.data_type_id = "trips"

		self.raw_data_path = os.path.join(
			data_paths_dict[self.city_name]["raw"][self.data_type_id],
			self.data_source_id,
		)

		self.norm_data_path = os.path.join(
			data_paths_dict[self.city_name]["norm"][self.data_type_id],
			self.data_source_id
		)
		check_create_path(self.norm_data_path)

		self.trips_df = pd.DataFrame()
		self.trips_df_norm = pd.DataFrame()

		if self.city_name == "Torino" or self.city_name == "Milano":
			self.tz = pytz.timezone("Europe/Rome")
		elif self.city_name == "Amsterdam":
			self.tz = pytz.timezone("Europe/Amsterdam")
		elif self.city_name == "Madrid":
			self.tz = pytz.timezone("Europe/Madrid")
		elif self.city_name == "Berlin":
			self.tz = pytz.timezone("Europe/Berlin")
		elif self.city_name == "New_York_City":
			self.tz = pytz.timezone("America/New_York")
		elif self.city_name == "Vancouver":
			self.tz = pytz.timezone("America/Vancouver")
		elif self.city_name == "Louisville":
			self.tz = pytz.timezone("America/Kentucky/Louisville")
		elif self.city_name == "Minneapolis":
			self.tz = pytz.timezone("America/Chicago")

	def load_raw(self):
		return

	def normalise(self):
		self.trips_df_norm = get_time_group_columns(self.trips_df_norm)
		return self.trips_df_norm

	def save_norm(self):
		for year in self.trips_df_norm.year.unique():
			for month in self.trips_df_norm.month.unique():

				trips_df_norm_year_month = self.trips_df_norm[
					(self.trips_df_norm.year == year) & (self.trips_df_norm.month == month)
				]
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

	def load_norm(self, year, month):
		data_path = os.path.join(
			data_paths_dict[self.city_name]["norm"][self.data_type_id],
			self.data_source_id,
			"_".join([str(year), str(month)]) + ".csv"
		)
		self.trips_df_norm = pd.read_csv(data_path, index_col=0)
		return self.trips_df_norm
