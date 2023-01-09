import argparse
import datetime

from odysseus.city_data_manager.geo_trips.nyc_open_data.nyc_citi_bike_geo_trips import NewYorkCityBikeGeoTrips
from odysseus.city_data_manager.geo_trips.big_data_db_polito.big_data_db_geo_trips import BigDataDBGeoTrips
from odysseus.city_data_manager.geo_trips.us_escooter_pilots.louisville_geo_trips import LouisvilleGeoTrips
from odysseus.city_data_manager.geo_trips.us_escooter_pilots.minneapolis_geo_trips import MinneapolisGeoTrips
from odysseus.city_data_manager.geo_trips.us_escooter_pilots.austin_geo_trips import AustinGeoTrips
from odysseus.city_data_manager.geo_trips.us_escooter_pilots.norfolk_geo_trips import NorfolkGeoTrips
from odysseus.city_data_manager.geo_trips.us_escooter_pilots.kansas_city_geo_trips import KansasCityGeoTrips
from odysseus.city_data_manager.geo_trips.us_escooter_pilots.chicago_geo_trips import ChicagoGeoTrips
from odysseus.city_data_manager.geo_trips.us_escooter_pilots.calgary_geo_trips import CalgaryGeoTrips
from odysseus.city_data_manager.geo_trips.enjoy.enjoy_geo_trips import EnjoyGeoTrips

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--cities", nargs="+",
    help="specify cities"
)

parser.add_argument(
    "-y", "--years", nargs="+",
    help="specify years"
)

parser.add_argument(
    "-m", "--months", nargs="+",
    help="specify months"
)

parser.add_argument(
    "-d", "--data_source_ids", nargs="+",
    help="specify data source ids"
)


parser.set_defaults(
    cities=["Torino"],
    data_source_ids=["big_data_db"],
    years=["2017"],
    months=["10"],
)

args = parser.parse_args()

for city in args.cities:
    for data_source_id in args.data_source_ids:
        for year in args.years:
            for month in args.months:
                print(datetime.datetime.now(), city, data_source_id, year, month)

                if data_source_id == "citi_bike":
                    geo_trips_ds = NewYorkCityBikeGeoTrips(year=int(year), month=int(month))

                elif data_source_id == "big_data_db":
                    geo_trips_ds = BigDataDBGeoTrips(city, data_source_id, year=int(year), month=int(month))

                elif data_source_id == "enjoy":
                    geo_trips_ds = EnjoyGeoTrips(city, data_source_id, year=int(year), month=int(month))

                elif data_source_id == "city_open_data":
                    if city == "Louisville":
                        geo_trips_ds = LouisvilleGeoTrips(year=int(year), month=int(month))
                    elif city == "Minneapolis":
                        geo_trips_ds = MinneapolisGeoTrips(year=int(year), month=int(month))
                    elif city == "Austin":
                        geo_trips_ds = AustinGeoTrips(year=int(year), month=int(month))
                    elif city == "Norfolk":
                        geo_trips_ds = NorfolkGeoTrips(year=int(year), month=int(month))
                    elif city == "Kansas City":
                        geo_trips_ds = KansasCityGeoTrips(year=int(year), month=int(month))
                    elif city == "Chicago":
                        geo_trips_ds = ChicagoGeoTrips(year=int(year), month=int(month))
                    elif city == "Calgary":
                        geo_trips_ds = CalgaryGeoTrips(year=int(year), month=int(month))

                geo_trips_ds.get_trips_od_gdfs()
                geo_trips_ds.save_points_data()
                geo_trips_ds.save_trips()

print(datetime.datetime.now(), "Done")
