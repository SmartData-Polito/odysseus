import os

import geopandas as gpd
import shapely

from odysseus.city_data_manager.config.config import *
from odysseus.utils.time_utils import *
from odysseus.utils.path_utils import *
from odysseus.utils.geospatial_utils import *


class CityGeoTrips:
	"""
	This abstract class deals with managing geographic travel information (e.g. departure, arrival, distance, etc.).
	This class is implemented by the other classes of this module. The constructor method takes as parameters:


	:param city_name: City name. The name also serves to determine the timezone to which the city belongs
	:type city_name: str
	:param trips_data_source_id: Data source from which the information is taken. This allows us to have multiple data sources associated with the same city (for example from different operators)
	:type trips_data_source_id: str
	:param year: year expressed as a four-digit number (e.g. 1999)
	:type year: int
	:param month: month expressed as a number (e.g. for November the method expects to receive 11)
	:type month: int
	"""

	def __init__(self, city_name, trips_data_source_id, year, month):

		self.city_name = city_name
		self.trips_data_source_id = trips_data_source_id
		self.year = year
		self.month = month

		self.trips_origins = gpd.GeoDataFrame()
		self.trips_destinations = gpd.GeoDataFrame()
		self.trips = gpd.GeoDataFrame()

		self.points_data_path = os.path.join(
			data_paths_dict[self.city_name]["od_trips"]["points"],
			self.trips_data_source_id,
			"_".join([str(self.year), str(self.month)]),
		)
		check_create_path(self.points_data_path)

		self.trips_data_path = os.path.join(
			data_paths_dict[self.city_name]["od_trips"]["trips"],
			self.trips_data_source_id,
			"_".join([str(self.year), str(self.month)]),
		)
		check_create_path(self.trips_data_path)

	def get_trips_od_gdfs(self):
		"""
		This method is used to store the movements, using the Shapely library. The normalized data is loaded
		(----> reference to save_norm magari<-----) and the method builds three GeoDataFrame.
		The trips are encoded using an object of the LineString class from the Shapely library. They are described
		as a segment having the coordinates of departure and arrival as extremes. In addition,
		two more GeoDataFrames are created, using objects of the Shapely.Point class to describe departures and arrivals.

		:return: nothing
		"""
		self.trips_ds_dict[self.trips_data_source_id].load_raw()
		self.trips_ds_dict[self.trips_data_source_id].normalise(self.year, self.month)

		self.trips_df_norm = self.trips_ds_dict[self.trips_data_source_id].load_norm(
			self.year, self.month
		)
		self.trips = self.trips_df_norm.copy()

		if len(self.trips):

			self.trips["geometry"] = self.trips_df_norm.apply(
				lambda row: shapely.geometry.LineString([
					shapely.geometry.Point(row["start_longitude"], row["start_latitude"]),
					shapely.geometry.Point(row["end_longitude"], row["end_latitude"]),
				]), axis=1
			)
			self.trips = gpd.GeoDataFrame(self.trips)
			self.trips.crs = "epsg:4326"

			self.trips_origins = self.trips_df_norm.copy()
			self.trips_destinations = self.trips_df_norm.copy()
			self.trips_origins["geometry"] = self.trips_origins.apply(
				lambda row: shapely.geometry.Point(row["start_longitude"], row["start_latitude"]), axis=1
			)
			self.trips_destinations["geometry"] = self.trips_destinations.apply(
				lambda row: shapely.geometry.Point(row["end_longitude"], row["end_latitude"]), axis=1
			)
			self.trips_origins = gpd.GeoDataFrame(self.trips_origins)
			self.trips_origins.crs = "epsg:4326"
			self.trips_destinations = gpd.GeoDataFrame(self.trips_destinations)
			self.trips_destinations.crs = "epsg:4326"

			print("gtod", self.trips.shape)

	def save_points(self, points, filename):
		"""
		Support method to save_data_points. It stores the points passed to it as a parameter both on csv file and on pickle.

		:param points: A GeoDataFrame describing the information of points to be saved
		:type points: geopandas.GeoDataFrame
		:param filename: Filename
		:type filename: str
		:return: nothing
		"""
		points.to_csv(
			os.path.join(
				self.points_data_path,
				filename + ".csv"
			)
		)
		points.to_pickle(
			os.path.join(
				self.points_data_path,
				filename + ".pickle"
			)
		)

	def save_points_data(self):
		"""
		Stores the points representing start and finish on file

		:return: nothing
		"""
		self.save_points(self.trips_origins, "origins")
		self.save_points(self.trips_destinations, "destinations")

	def save_trips(self):
		"""
		It stores on file the segments that represent the path between start and finish

		:return: nothing
		"""
		self.trips.to_csv(
			os.path.join(
				self.trips_data_path,
				"trips.csv"
			)
		)
		self.trips.to_pickle(
			os.path.join(
				self.trips_data_path,
				"trips.pickle"
			)
		)

	def load(self):
		"""
		Load from memory, using the pickle file created by the save methods, the three GeoDataFrame

		:return: nothing
		"""
		self.trips_origins = get_time_group_columns(pd.read_pickle(
			os.path.join(
				self.points_data_path,
				"origins.pickle"
			)
		))
		self.trips_destinations = get_time_group_columns(pd.read_pickle(
			os.path.join(
				self.points_data_path,
				"destinations.pickle"
			)
		))
		self.trips = get_time_group_columns(pd.read_pickle(
			os.path.join(
				self.trips_data_path,
				"trips.pickle"
			)
		))

