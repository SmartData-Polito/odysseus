import pandas as pd

from e3f2s.city_data_manager.city_data_source.trips_data_source.louisville_scooter_trips import LouisvilleScooterTrips
from e3f2s.city_data_manager.city_geo_trips.city_geo_trips import CityGeoTrips


class LouisvilleGeoTrips(CityGeoTrips):

	def __init__(self, trips_data_source_id, year, month, bin_side_length):

		self.city_name = "Louisville"
		super().__init__(self.city_name, trips_data_source_id, year, month, bin_side_length)
		self.trips_ds_dict = {
			"city_of_louisville": LouisvilleScooterTrips()
		}
		self.trips_df_norm = pd.DataFrame()
