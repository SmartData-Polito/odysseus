import pandas as pd
import geopandas as gpd
import shapely

from e3f2s.city_data_manager.city_data_source.trips_data_source.new_york_city_bikes_trips import NewYorkCityBikeTrips
from e3f2s.city_data_manager.city_geo_trips.city_geo_trips import CityGeoTrips


class NewYorkCityBikeGeoTrips(CityGeoTrips):

	def __init__(self, city_name="New_York_City", trips_data_source_id="citi_bike", year=2017, month=1):

		self.city_name = city_name
		super().__init__(self.city_name, trips_data_source_id, year, month)
		self.trips_ds_dict = {
			"citi_bike": NewYorkCityBikeTrips(city_name)
		}
		self.trips_df_norm = pd.DataFrame()

	def get_trips_od_gdfs(self):

		self.trips_ds_dict[self.trips_data_source_id].load_raw(self.year, self.month)
		self.trips_ds_dict[self.trips_data_source_id].normalise(self.year, self.month)
