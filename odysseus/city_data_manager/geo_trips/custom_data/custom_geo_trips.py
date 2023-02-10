import pandas as pd

from odysseus.city_data_manager.geo_trips.custom_data.custom_trips import CustomTrips

from odysseus.city_data_manager.geo_trips.city_geo_trips import CityGeoTrips


class CustomGeoTrips(CityGeoTrips):

	def __init__(self, city_name, trips_data_source_id, year, month):

		self.city_name = city_name
		super().__init__(self.city_name, trips_data_source_id, year, month)
		self.trips_ds_dict = {
			"custom_trips": CustomTrips(city_name)
		}
		self.trips_df_norm = pd.DataFrame()
