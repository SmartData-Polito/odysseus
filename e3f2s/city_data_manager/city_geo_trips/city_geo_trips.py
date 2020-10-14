import os

import geopandas as gpd
import shapely

from e3f2s.city_data_manager.config.config import *
from e3f2s.utils.time_utils import *
from e3f2s.utils.path_utils import *
from e3f2s.utils.geospatial_utils import *


class CityGeoTrips:

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

		self.trips_ds_dict[self.trips_data_source_id].load_raw()
		self.trips_ds_dict[self.trips_data_source_id].normalise(self.year, self.month)

		self.trips_df_norm = self.trips_ds_dict[self.trips_data_source_id].load_norm(
			self.year, self.month
		)
		self.trips = self.trips_df_norm.copy()
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

	def save_points(self, points, filename):
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
		self.save_points(self.trips_origins, "origins")
		self.save_points(self.trips_destinations, "destinations")

	def save_trips(self):
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
				"raw.pickle"
			)
		))

