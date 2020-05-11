import pandas as pd
import geopandas as gpd
import shapely

from city_data_manager.city_data_source.trips_data_source.big_data_db_trips import BigDataDBTrips

from city_data_manager.city_geo_trips.city_geo_trips import CityGeoTrips


class BigDataDBGeoTrips(CityGeoTrips):

	def __init__(self, city_name, trips_data_source_id, year, month, bin_side_length):

		self.city_name = city_name
		super().__init__(self.city_name, trips_data_source_id, year, month, bin_side_length)
		self.trips_ds_dict = {
			"big_data_db": BigDataDBTrips(city_name)
		}
		self.trips_df_norm = pd.DataFrame()

	def get_trips_od_gdfs(self):

		self.trips_ds_dict[self.trips_data_source_id].load_raw()
		self.trips_ds_dict[self.trips_data_source_id].normalise()

		self.trips_df_norm = self.trips_ds_dict[self.trips_data_source_id].load_norm(
			self.year, self.month
		)
		self.trips_origins = self.trips_df_norm.copy()
		self.trips_origins.drop([col for col in self.trips_origins if "end" in col], axis=1, inplace=True)
		self.trips_destinations = self.trips_df_norm.copy()
		self.trips_destinations.drop([col for col in self.trips_destinations if "start" in col], axis=1, inplace=True)

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

		self.trips_df_norm["euclidean_distance"] = (
			self.trips_origins.distance(self.trips_destinations) * 111.32 / 0.001
		)

