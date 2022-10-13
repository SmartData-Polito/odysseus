import pandas as pd

from odysseus.city_data_manager.geo_trips.enjoy.enjoy_trips import EnjoyTrips

from odysseus.city_data_manager.geo_trips.city_geo_trips import CityGeoTrips


class EnjoyGeoTrips(CityGeoTrips):

	def __init__(self, city_name, trips_data_source_id, year, month):

		self.city_name = city_name
		super().__init__(self.city_name, trips_data_source_id, year, month)
		self.trips_ds_dict = {
			"enjoy": EnjoyTrips(city_name)
		}
		self.trips_df_norm = pd.DataFrame()
