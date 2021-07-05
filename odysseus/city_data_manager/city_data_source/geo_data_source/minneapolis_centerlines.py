import os

import geopandas as gpd

from odysseus.city_data_manager.city_data_source.geo_data_source.geo_data_source import GeoDataSource


class MinneapolisCenterlines(GeoDataSource):

	def __init__(self):
		super().__init__("Minneapolis", "mpls_centerlines")

	def load_raw(self):
		raw_geo_data_path = os.path.join(
			self.raw_data_path,
			"MPLS_Centerline.dbf"
		)
		gdf = gpd.read_file(raw_geo_data_path)
		self.gdf = gdf
		return self.gdf

	def normalise(self):

		gdf_norm = self.load_raw()
		gdf_norm = gdf_norm.rename({
			"GBSID":"centerline_id"
		}, axis=1)
		gdf_norm = gdf_norm[[
			"centerline_id", "geometry"
		]]
		gdf_norm.centerline_id = gdf_norm.centerline_id.astype(str)

		gdf_norm.to_file(
			os.path.join(
				self.norm_data_path,
				"centerlines.shp"
			)
		)

		self.gdf_norm = gdf_norm
		return gdf_norm
