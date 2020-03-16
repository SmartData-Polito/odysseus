import pandas as pd
import geopandas as gpd

from city_data_manager.city_data_source.trips_data_source.minneapolis_scooter_trips import MinneapolisScooterTrips
from city_data_manager.city_data_source.geo_data_source.minneapolis_centerlines import MinneapolisCenterlines
from city_data_manager.city_data_source.geo_data_source.minneapolis_trails_bikes import MinneapolisTrailsBikes
from city_data_manager.city_data_source.utils.geospatial_utils import get_random_point_from_linestring
from city_data_manager.city_geo_trips.city_geo_trips import CityGeoTrips


class MinneapolisGeoTrips(CityGeoTrips):

	def __init__(self, trips_data_source_id, year, month, bin_side_length):

		self.city_name = "Minneapolis"
		super().__init__(self.city_name, trips_data_source_id, year, month, bin_side_length)
		self.trips_ds_dict = {
			"city_of_minneapolis": MinneapolisScooterTrips()
		}
		self.trips_df_norm = pd.DataFrame()

		self.trails_ds = MinneapolisTrailsBikes()
		self.trails_ds.normalise()
		self.trails_gdf_norm = self.trails_ds.gdf_norm

		self.centerlines_ds = MinneapolisCenterlines()
		self.centerlines_ds.normalise()
		self.centerlines_gdf_norm = self.centerlines_ds.gdf_norm

	def get_trips_od_gdfs(self):

		self.trips_ds_dict[self.trips_data_source_id].load_raw(self.year, self.month)
		self.trips_ds_dict[self.trips_data_source_id].normalise()


		self.trips_df_norm = self.trips_ds_dict[self.trips_data_source_id].load_norm(
			self.year, self.month
		)
		trips_origins_trails = self.trips_df_norm.loc[
			self.trips_df_norm.start_centerline_id.isin(
				self.trails_gdf_norm.trail_id
		)]
		trips_destinations_trails = self.trips_df_norm.loc[
			self.trips_df_norm.end_centerline_id.isin(
				self.trails_gdf_norm.trail_id
		)]
		trips_origins_centerlines_index = self.trips_df_norm.index.difference(
			trips_origins_trails
		)
		trips_destinations_centerlines_index = self.trips_df_norm.index.difference(
			trips_destinations_trails
		)
		self.trips_df_norm.start_centerline_id = self.trips_df_norm.start_centerline_id.astype(str)
		self.trips_df_norm.end_centerline_id = self.trips_df_norm.end_centerline_id.astype(str)

		trips_origins_centerlines = self.trips_df_norm.loc[trips_origins_centerlines_index]
		trips_origins_centerlines.start_centerline_id = trips_origins_centerlines.start_centerline_id.apply(
				lambda string: string.split(".")[0]
			)
		trips_destinations_centerlines = self.trips_df_norm.loc[trips_destinations_centerlines_index]
		trips_destinations_centerlines.end_centerline_id = trips_destinations_centerlines.end_centerline_id.apply(
				lambda string: string.split(".")[0]
			)

		trips_origins_centerlines = gpd.GeoDataFrame(pd.merge(
			trips_origins_centerlines,
			self.centerlines_gdf_norm,
			left_on="start_centerline_id", right_on="centerline_id"
		))
		if len(trips_origins_trails):
			trips_origins_trails = gpd.GeoDataFrame(pd.merge(
				trips_origins_trails,
				self.trails_gdf_norm,
				left_on="start_centerline_id", right_on="trail_id"
			))
		print(trips_origins_trails.shape, trips_origins_centerlines.shape)
		self.trips_origins = pd.concat([
			trips_origins_centerlines,
			#trips_origins_trails
		], sort=False)
		self.trips_origins.geometry = self.trips_origins.geometry.apply(
			get_random_point_from_linestring
		)
		self.trips_origins.crs = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"

		trips_destinations_centerlines = gpd.GeoDataFrame(pd.merge(
			trips_destinations_centerlines,
			self.centerlines_gdf_norm,
			left_on="end_centerline_id", right_on="centerline_id"
		))
		if len(trips_destinations_trails):
			trips_destinations_trails = gpd.GeoDataFrame(pd.merge(
				trips_destinations_trails,
				self.trails_gdf_norm,
				left_on="end_centerline_id", right_on="trail_id"
			))
		print(trips_destinations_trails.shape, trips_destinations_centerlines.shape)
		self.trips_destinations = pd.concat([
			trips_destinations_centerlines,
			#trips_destinations_trails
		], sort=False)
		self.trips_destinations.geometry = self.trips_destinations.geometry.apply(
			get_random_point_from_linestring
		)
		self.trips_destinations.crs = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"

