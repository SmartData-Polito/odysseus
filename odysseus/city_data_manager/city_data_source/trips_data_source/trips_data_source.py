import os
import pytz
import pandas as pd

from odysseus.city_data_manager.config.config import *
from odysseus.utils.path_utils import check_create_path
from odysseus.utils.time_utils import get_time_group_columns


class TripsDataSource:
	"""
	TripsDataSource is an abstract class that contains the information needed to describe a trip.
	This class is implemented by the other classes of this module. The constructor method takes as parameters:

    :param city_name: City name. The name also serves to determine the timezone to which the city belongs
    :type city_name: str
    :param data_source_id: Data source from which the information is taken. This allows us to have multiple data sources associated with the same city (for example from different operators)
    :type data_source_id: str
    :param vehicles_type_id: Type of service represented by the data source (e.g. car sharing or e-scooter)
    :type vehicles_type_id: str
    """

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

		if self.city_name == "Roma" or self.city_name == "Torino" or self.city_name == "Milano":
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
		elif self.city_name == "Minneapolis" or self.city_name == "Chicago":
			self.tz = pytz.timezone("America/Chicago")
		elif self.city_name == "Austin" or self.city_name == "Kansas City":
			self.tz = pytz.timezone("US/Central")
		elif self.city_name == "Norfolk":
			self.tz = pytz.timezone("US/Eastern")
		elif self.city_name == "Calgary":
			self.tz = pytz.timezone("Canada/Mountain")

	def load_raw(self):
		"""
		Method for loading the data to be preprocessed. Since the data format differs in the various datasets, the method
		is left abstract. Each city has its own implementation. All implementations will read the data through the pandas readcsv method

		:return: nothing
		"""
		return

	def normalise(self):
		"""
		This method is used to standardize the data format. Again the implementation is highly dependent on the data
		source and almost all modules override the method.

		:return: A normalized pandas.DataFrame
		"""
		self.trips_df_norm = get_time_group_columns(self.trips_df_norm)
		return self.trips_df_norm

	def save_norm(self):
		"""
		It stores normalized data both in a csv file and in a pickle file. The files produced are of the format
		*<year>_<month number>.csv* (or .pickle). For example *2017_11.csv*.

		:return: nothing
		"""
		print(self.trips_df_norm.shape)

		for year in self.trips_df_norm.start_year.unique():
			for month in self.trips_df_norm.start_month.unique():

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

	def load_norm(self, year, month):
		"""
		Load a previously created normalized file from memory. It requests month and year as parameters, and checks if
		the file for that period exists in memory (looking for it with the same format as *save_norm* in the city folder).
		If it exists, it returns a pandas.DataFrame containing the data read, otherwise it returns an empty DataFrame

		:param year: year expressed as a four-digit number (e.g. 1999)
		:type year: int
		:param month: month expressed as a number (e.g. for November the method expects to receive 11)
		:type month: int
		:return: If the file exists, it returns a pandas.DataFrame containing the data read, otherwise it returns an empty DataFrame
		"""
		data_path = os.path.join(
			data_paths_dict[self.city_name]["norm"][self.data_type_id],
			self.data_source_id,
			"_".join([str(year), str(month)]) + ".csv"
		)
		if os.path.exists(data_path):
			self.trips_df_norm = pd.read_csv(data_path).iloc[:, 1:]
			return self.trips_df_norm
		else:
			return pd.DataFrame()
