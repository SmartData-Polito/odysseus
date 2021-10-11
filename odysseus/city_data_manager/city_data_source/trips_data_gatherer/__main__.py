import os
from odysseus.city_data_manager.config.config import data_paths_dict
from odysseus.city_data_manager.city_data_source.trips_data_gatherer.citi_bike_data_gatherer import CitiBikeDataGatherer

# raw_data_path = os.path.join(data_paths_dict["New_York_City"]["raw"]["trips"], "citi_bike")
# os.makedirs(raw_data_path, exist_ok=True)
#
# for month in range(1, 2):
#     gatherer = CitiBikeDataGatherer(raw_data_path)
#     gatherer.download_data(2017, month)

from odysseus.city_data_manager.city_data_source.trips_data_gatherer.louisville_scooter_trips_gatherer import LouisvilleScooterDataGatherer

raw_data_path = os.path.join(data_paths_dict["Louisville"]["raw"]["trips"], "city_open_data")
os.makedirs(raw_data_path, exist_ok=True)

gatherer = LouisvilleScooterDataGatherer(
    raw_data_path,
)
gatherer.download_data()
