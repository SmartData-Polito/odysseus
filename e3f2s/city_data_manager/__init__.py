import pandas as gpd
from pathlib import Path
from e3f2s.city_data_manager.city_data_source.trips_data_gatherer.citi_bike_data_gatherer import DataGatherer

cb_dg = DataGatherer('./data/New_York_City/raw/trips/citi_bike',
                     "citibike-tripdata.csv")

# TODO: for some reason is called twice
cb_dg.download_data(2017,1)
cb_dg.standarzide_data(2017,1)
