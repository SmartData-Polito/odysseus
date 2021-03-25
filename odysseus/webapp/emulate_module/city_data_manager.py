import argparse
import datetime

from e3f2s.city_data_manager.city_geo_trips.nyc_citi_bike_geo_trips import NewYorkCityBikeGeoTrips
from e3f2s.city_data_manager.city_geo_trips.big_data_db_geo_trips import BigDataDBGeoTrips
from e3f2s.city_data_manager.city_geo_trips.louisville_geo_trips import LouisvilleGeoTrips
from e3f2s.city_data_manager.city_geo_trips.minneapolis_geo_trips import MinneapolisGeoTrips
from e3f2s.city_data_manager.city_geo_trips.austin_geo_trips import AustinGeoTrips
from e3f2s.city_data_manager.city_geo_trips.norfolk_geo_trips import NorfolkGeoTrips
from e3f2s.city_data_manager.city_geo_trips.kansas_city_geo_trips import KansasCityGeoTrips
from e3f2s.city_data_manager.city_geo_trips.chicago_geo_trips import ChicagoGeoTrips
from e3f2s.city_data_manager.city_geo_trips.calgary_geo_trips import CalgaryGeoTrips
from e3f2s.webapp.apis.api_cityDataManager.data_transormer_cdm.transformer_cdm import DataTransformer

class CityDataManager():
    def __init__(self,cities=["Torino"],years=[2017],months=["10","11"],data_source_ids=["big_data_db"]):
        self.cities=cities
        self.years = years
        self.months = months
        self.data_source_ids = data_source_ids
        self.dt = DataTransformer()

    def run(self):
        for city in self.cities:
            for data_source_id in self.data_source_ids:
                for year in self.years:
                    for month in self.months:
                        print(datetime.datetime.now(), city, data_source_id, year, month)

                        if data_source_id == "citi_bike":
                            geo_trips_ds = NewYorkCityBikeGeoTrips(year=int(year), month=int(month))

                        elif data_source_id == "big_data_db":
                            geo_trips_ds = BigDataDBGeoTrips(city, data_source_id, year=int(year), month=int(month))

                        elif data_source_id == "city_open_data":
                            if city == "city_of_louisville":
                                geo_trips_ds = LouisvilleGeoTrips(year=int(year), month=int(month))

                            elif city == "city_of_minneapolis":
                                geo_trips_ds = MinneapolisGeoTrips(year=int(year), month=int(month))

                            elif city == "city_of_austin":
                                geo_trips_ds = AustinGeoTrips(year=int(year), month=int(month))

                            elif city == "city_of_norfolk":
                                geo_trips_ds = NorfolkGeoTrips(year=int(year), month=int(month))

                            elif city == "city_of_kansas_city":
                                geo_trips_ds = KansasCityGeoTrips(year=int(year), month=int(month))

                            elif city == "city_of_chicago":
                                geo_trips_ds = ChicagoGeoTrips(year=int(year), month=int(month))

                            elif city == "city_of_calgary":
                                geo_trips_ds = CalgaryGeoTrips(year=int(year), month=int(month))

                        geo_trips_ds.get_trips_od_gdfs()
                        geo_trips_ds.save_points_data()
                        geo_trips_ds.save_trips()
                        self.dt.save_to_db(city,data_source_id, year, month)
        print(datetime.datetime.now(), "Done")
