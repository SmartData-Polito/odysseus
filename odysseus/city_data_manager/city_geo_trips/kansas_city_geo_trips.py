import pandas as pd
import geopandas as gpd

from shapely.geometry import LineString, Point

from odysseus.city_data_manager.city_data_source.trips_data_source.kansas_city_scooter_trips import KansasCityScooterTrips
from odysseus.city_data_manager.city_geo_trips.city_geo_trips import CityGeoTrips


class KansasCityGeoTrips(CityGeoTrips):

    def __init__(self, city_name="Kansas City", trips_data_source_id="city_open_data", year=2019, month=7):

        self.city_name = city_name
        super().__init__(self.city_name, trips_data_source_id, year, month)
        self.trips_ds_dict = {
            "city_open_data": KansasCityScooterTrips()
        }
        self.trips_df_norm = pd.DataFrame()
