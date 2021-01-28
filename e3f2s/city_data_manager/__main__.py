import argparse
import datetime

from e3f2s.city_data_manager.city_geo_trips.nyc_citi_bike_geo_trips import NewYorkCityBikeGeoTrips
from e3f2s.city_data_manager.city_geo_trips.big_data_db_geo_trips import BigDataDBGeoTrips

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
    cities=["Torino", "Milano", "Vancouver"],
    data_source_ids=["big_data_db"],
    years=["2017"],
    months=["10", "11", "12"],
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

                geo_trips_ds.get_trips_od_gdfs()
                geo_trips_ds.save_points_data()
                geo_trips_ds.save_trips()

print(datetime.datetime.now(), "Done")
