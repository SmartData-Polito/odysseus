import os

import geopandas as gpd

from odysseus.city_data_manager.config.config import data_paths_dict
from odysseus.utils.path_utils import check_create_path


class GeoDataSource:
	"""
	This abstract class is used only for data sources that represent the place of departure and arrival without GPS coordinates.
	For example, the Minneapolis-related data they contain are stored in reference to the Centerline MPLS system.
	In order to correctly interpret these data we use this class that normalizes them and stores them in a shapefile

	:param city_id: City name. The name also serves to determine the timezone to which the city belongs
	:type city_id: str
	:param data_source_id: Data source from which the information is taken. This allows us to have multiple data sources associated with the same city (for example from different operators)
	:type data_source_id: str
			"""
	def __init__(self, city_id, data_source_id):

		self.city_id = city_id
		self.data_source_id = data_source_id
		self.data_type_id = "geo"

		self.raw_data_path = os.path.join(
			data_paths_dict[self.city_id]["raw"][self.data_type_id],
			self.data_source_id,
		)

		self.norm_data_path = os.path.join(
			data_paths_dict[self.city_id]["norm"][self.data_type_id],
			self.data_source_id
		)
		check_create_path(self.norm_data_path)

		self.gdf = gpd.GeoDataFrame()
		self.gdf_norm = gpd.GeoDataFrame()

	def load_raw(self):
		"""
		Abstract method that opens the file describing the geometry of the city

		:return: nothing
				"""
		return

	def normalise(self):
		"""
		Abstract method that normalizes the data and stores the created shapefiles

		:return: nothing
				"""
		return
