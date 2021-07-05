import os

import geopandas as gpd

from odysseus.city_data_manager.city_data_source.geo_data_source.geo_data_source import GeoDataSource

from shapely import ops


class MinneapolisTrailsBikes(GeoDataSource):

	def __init__(self):
		super().__init__("Minneapolis", "mpls_trails_bikes")

	def load_raw(self):
		raw_geo_data_path = os.path.join(
			self.raw_data_path,
			"MetroCollaborativeTrailsBikeways.dbf"
		)
		gdf = gpd.read_file(raw_geo_data_path)
		self.gdf = gdf
		return self.gdf

	def normalise(self):

		self.gdf_norm = self.load_raw()
		self.gdf_norm = self.gdf_norm.rename({
			"UNIQUE_ID": "trail_id"
		}, axis=1)
		self.gdf_norm = self.gdf_norm[[
			"trail_id", "geometry"
		]]

		self.gdf_norm.loc[
			self.gdf_norm.geometry.geom_type == "MultiLineString", "geometry"
		] = self.gdf_norm.loc[
				self.gdf_norm.geometry.geom_type == "MultiLineString", "geometry"
			].geometry.apply(lambda x: ops.linemerge(x))

		self.gdf_norm.to_file(
			os.path.join(
				self.norm_data_path,
				"trails.shp"
			)
		)

		return self.gdf_norm
