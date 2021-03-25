import pandas as pd

from odysseus.city_data_manager.city_data_source.trips_data_source.big_data_db_trips import BigDataDBTrips

from odysseus.city_data_manager.city_geo_trips.city_geo_trips import CityGeoTrips


class BigDataDBGeoTrips(CityGeoTrips):

	def __init__(self, city_name, trips_data_source_id, year, month):

		self.city_name = city_name
		super().__init__(self.city_name, trips_data_source_id, year, month)
		self.trips_ds_dict = {
			"big_data_db": BigDataDBTrips(city_name)
		}
		self.trips_df_norm = pd.DataFrame()
