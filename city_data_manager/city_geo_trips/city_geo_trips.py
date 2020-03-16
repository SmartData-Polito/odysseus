import os

import pandas as pd
import geopandas as gpd

from city_data_manager.config.config import data_paths_dict
from city_data_manager.city_data_source.utils.path_utils import check_create_path
from city_data_manager.city_data_source.utils.geospatial_utils import get_city_grid
from city_data_manager.city_data_source.utils.geospatial_utils import add_grouped_count_to_grid
from city_data_manager.city_data_source.utils.time_utils import get_grouped_resampled_count
from city_data_manager.city_data_source.utils.time_utils import get_time_group_columns


class CityGeoTrips:

	def __init__(self, city_name, trips_data_source_id, year, month, bin_side_length):

		self.city_name = city_name
		self.trips_data_source_id = trips_data_source_id
		self.year = year
		self.month = month

		self.trips_origins = gpd.GeoDataFrame()
		self.trips_destinations = gpd.GeoDataFrame()
		self.squared_grid = gpd.GeoDataFrame()

		self.points_data_path = os.path.join(
			data_paths_dict[self.city_name],
			"_".join([str(self.year), str(self.month)]),
			self.trips_data_source_id,
			str(bin_side_length),
			"points",
		)
		check_create_path(self.points_data_path)

		self.od_trips_data_path = os.path.join(
			data_paths_dict[self.city_name],
			"_".join([str(self.year), str(self.month)]),
			self.trips_data_source_id,
			str(bin_side_length),
			"od_trips",
		)
		check_create_path(self.od_trips_data_path)

		self.squared_grid_data_path = os.path.join(
			data_paths_dict[self.city_name],
			"_".join([str(self.year), str(self.month)]),
			self.trips_data_source_id,
			str(bin_side_length),
			"squared_grid",
		)
		check_create_path(self.squared_grid_data_path)

		self.resampled_points_data_path = os.path.join(
			data_paths_dict[self.city_name],
			"_".join([str(self.year), str(self.month)]),
			self.trips_data_source_id,
			str(bin_side_length),
			"resampled_points",
		)
		check_create_path(self.resampled_points_data_path)

		self.bin_side_length = bin_side_length

	def get_squared_grid (self):

		locations = pd.concat([
				self.trips_origins.geometry, self.trips_destinations.geometry
		], ignore_index=True)
		locations.crs = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
		self.squared_grid = get_city_grid(
			locations,
			self.bin_side_length
		)
		return self.squared_grid

	def map_zones_on_trips(self, zones):
		self.trips_origins = gpd.sjoin(
			self.trips_origins,
			zones,
			how='left',
			op='within'
		)
		self.trips_destinations = gpd.sjoin(
			self.trips_destinations,
			zones,
			how='left',
			op='within'
		)
		self.od_trips_df = self.trips_df_norm.copy()
		self.od_trips_df["origin_id"] = self.trips_origins.zone_id
		self.od_trips_df["destination_id"] = self.trips_destinations.zone_id

	def map_trips_on_zones(self, zones):
		zones = add_grouped_count_to_grid(
			zones, self.trips_origins, "start_hour", "o"
		)
		zones = add_grouped_count_to_grid(
			zones, self.trips_destinations, "end_hour", "d"
		)
		return zones

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

	def save_squared_grid(self):
		self.squared_grid.to_csv(
			os.path.join(
				self.squared_grid_data_path,
				str(self.bin_side_length) + ".csv"
			)
		)
		self.squared_grid.to_pickle(
			os.path.join(
				self.squared_grid_data_path,
				str(self.bin_side_length) + ".pickle"
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
		self.squared_grid = pd.read_pickle(
			os.path.join(
				self.squared_grid_data_path,
				str(self.bin_side_length) + ".pickle"
			)
		)

	def get_resampled_points_count_by_zone(self, group_cols, freq):
		self.resampled_origins = get_grouped_resampled_count(
			self.trips_origins,
			group_cols,
			freq
		)

	def save_resampled_points(self, points, filename):
		points.to_csv(
			os.path.join(
				self.resampled_points_data_path,
				filename + ".csv"
			)
		)
		points.to_pickle(
			os.path.join(
				self.resampled_points_data_path,
				filename + ".pickle"
			)
		)

	def save_resampled_points_data(self):
		self.save_resampled_points(self.resampled_origins, "origins")

	def load_resampled(self):
		self.resampled_origins = pd.read_pickle(
			os.path.join(
				self.resampled_points_data_path,
				"origins.pickle"
			)
		)

	def save_od_trips(self, od_trips, filename):
		od_trips.to_csv(
			os.path.join(
				self.od_trips_data_path,
				filename + ".csv"
			)
		)
		od_trips.to_pickle(
			os.path.join(
				self.od_trips_data_path,
				filename + ".pickle"
			)
		)
