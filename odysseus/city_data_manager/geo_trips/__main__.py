import argparse
import datetime

from odysseus.city_data_manager.geo_trips.custom_data.custom_geo_trips import CustomGeoTrips

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
    cities=["test_city"],
    data_source_ids=["custom_trips"],
    years=["2020"],
    months=["9"],
)

args = parser.parse_args()

for city in args.cities:
    for data_source_id in args.data_source_ids:
        for year in args.years:
            for month in args.months:

                print(datetime.datetime.now(), city, data_source_id, year, month)

                if data_source_id == "custom_trips":
                    geo_trips_ds = CustomGeoTrips(city, data_source_id, year=int(year), month=int(month))
                    geo_trips_ds.get_trips_od_gdfs()
                    geo_trips_ds.save_points_data()
                    geo_trips_ds.save_trips()

print(datetime.datetime.now(), "Done")
