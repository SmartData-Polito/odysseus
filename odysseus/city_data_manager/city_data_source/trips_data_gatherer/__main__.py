import argparse

import os
from odysseus.path_config.path_config import data_paths_dict

from odysseus.city_data_manager.city_data_source.trips_data_gatherer.citi_bike_data_gatherer\
    import CitiBikeDataGatherer
from odysseus.city_data_manager.city_data_source.trips_data_gatherer.louisville_scooter_trips_gatherer\
    import LouisvilleScooterDataGatherer
from odysseus.city_data_manager.city_data_source.trips_data_gatherer.austin_scooter_trips_gatherer\
    import AustinScooterDataGatherer, AustinScooterGeoDataGatherer
from odysseus.city_data_manager.city_data_source.trips_data_gatherer.calgary_scooter_trips_gatherer\
    import CalgaryScooterDataGatherer, CalgaryScooterGeoDataGatherer
from odysseus.city_data_manager.city_data_source.trips_data_gatherer.chicago_scooter_trips_gatherer\
    import ChicagoScooterDataGatherer, ChicagoScooterGeoDataGatherer1, ChicagoScooterGeoDataGatherer2


parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--cities", nargs="+",
    help="specify cities"
)

parser.set_defaults(
    cities=["Louisville"],
)

args = parser.parse_args()
for city in args.cities:
    if city == "New_York_City":
        for month in range(1, 2):
            raw_data_path = os.path.join(data_paths_dict["New_York_City"]["raw"]["trips"], "citi_bike")
            os.makedirs(raw_data_path, exist_ok=True)
            gatherer = CitiBikeDataGatherer(raw_data_path)
            gatherer.download_data(2017, month)
    elif city == "Louisville":
        raw_data_path = os.path.join(data_paths_dict["Louisville"]["raw"]["trips"], "city_open_data")
        os.makedirs(raw_data_path, exist_ok=True)
        gatherer = LouisvilleScooterDataGatherer(raw_data_path)
        gatherer.download_data()
    elif city == "Austin":
        raw_data_path = os.path.join(data_paths_dict["Austin"]["raw"]["trips"], "city_open_data")
        os.makedirs(raw_data_path, exist_ok=True)
        gatherer = AustinScooterDataGatherer(raw_data_path)
        gatherer.download_data()
        raw_data_path = os.path.join(data_paths_dict["Austin"]["raw"]["geo"], "us_census_bureau")
        os.makedirs(raw_data_path, exist_ok=True)
        gatherer = AustinScooterGeoDataGatherer(raw_data_path)
        gatherer.download_data()
    elif city == "Calgary":
        raw_data_path = os.path.join(data_paths_dict["Calgary"]["raw"]["trips"], "city_open_data")
        os.makedirs(raw_data_path, exist_ok=True)
        gatherer = CalgaryScooterDataGatherer(raw_data_path)
        gatherer.download_data()
        raw_data_path = os.path.join(data_paths_dict["Calgary"]["raw"]["geo"], "city_open_data")
        os.makedirs(raw_data_path, exist_ok=True)
        gatherer = CalgaryScooterGeoDataGatherer(raw_data_path)
        gatherer.download_data()

    elif city == "Chicago":
        # raw_data_path = os.path.join(data_paths_dict["Chicago"]["raw"]["trips"], "city_open_data")
        # os.makedirs(raw_data_path, exist_ok=True)
        # gatherer = ChicagoScooterDataGatherer(raw_data_path)
        # gatherer.download_data()
        raw_data_path = os.path.join(data_paths_dict["Chicago"]["raw"]["geo"], "us_census_bureau")
        os.makedirs(raw_data_path, exist_ok=True)
        gatherer = ChicagoScooterGeoDataGatherer1(raw_data_path)
        gatherer.download_data()
        raw_data_path = os.path.join(data_paths_dict["Chicago"]["raw"]["geo"], "city_open_data")
        os.makedirs(raw_data_path, exist_ok=True)
        gatherer = ChicagoScooterGeoDataGatherer2(raw_data_path)
        gatherer.download_data()
