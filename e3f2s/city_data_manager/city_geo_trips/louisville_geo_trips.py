import pandas as pd

from e3f2s.city_data_manager.city_data_source.trips_data_source.louisville_scooter_trips import LouisvilleScooterTrips
from e3f2s.city_data_manager.city_geo_trips.city_geo_trips import CityGeoTrips


class LouisvilleGeoTrips(CityGeoTrips):

	def __init__(self, city_name="Louisville", trips_data_source_id="city_of_louisville", year=2019, month=7):

		self.city_name = city_name
		super().__init__(self.city_name, trips_data_source_id, year, month)
		self.trips_ds_dict = {
			"city_of_louisville": LouisvilleScooterTrips()
		}
		self.trips_df_norm = pd.DataFrame()
