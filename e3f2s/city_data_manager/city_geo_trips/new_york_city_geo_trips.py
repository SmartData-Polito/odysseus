import pandas as pd
import geopandas as gpd
import shapely

from e3f2s.city_data_manager.city_data_source.trips_data_source.new_york_city_bikes_trips import NewYorkCityBikeTrips

from e3f2s.city_data_manager.city_geo_trips.city_geo_trips import CityGeoTrips


class BigDataDBGeoTrips(CityGeoTrips):

    def __init__(self, city_name, trips_data_source_id, year, month):

        self.city_name = city_name
        super().__init__(self.city_name, trips_data_source_id, year, month)
        self.trips_ds_dict = {
            "city_of_new_york_city": NewYorkCityBikeTrips(city_name)
        }
        self.trips_df_norm = pd.DataFrame()

    def get_trips_od_gdfs(self):

        self.trips_ds_dict[self.trips_data_source_id].load_raw()
        self.trips_ds_dict[self.trips_data_source_id].normalise(self.year, self.month)

        self.trips_df_norm = self.trips_ds_dict[self.trips_data_source_id].load_norm(
            self.year, self.month
        )
        self.trips = self.trips_df_norm.copy()
        self.trips["geometry"] = self.trips_df_norm.apply(
            lambda row: shapely.geometry.LineString([
                shapely.geometry.Point(row["start_longitude"], row["start_latitude"]),
                shapely.geometry.Point(row["end_longitude"], row["end_latitude"]),
            ]), axis=1
        )
        self.trips = gpd.GeoDataFrame(self.trips)
        self.trips.crs = "epsg:4326"

        self.trips_origins = self.trips_df_norm.copy()
        self.trips_origins.drop([col for col in self.trips_origins if "end" in col], axis=1, inplace=True)
        self.trips_destinations = self.trips_df_norm.copy()
        self.trips_destinations.drop([col for col in self.trips_destinations if "start" in col], axis=1, inplace=True)
        self.trips_origins["geometry"] = self.trips_origins.apply(
            lambda row: shapely.geometry.Point(row["start_longitude"], row["start_latitude"]), axis=1
        )
        self.trips_destinations["geometry"] = self.trips_destinations.apply(
            lambda row: shapely.geometry.Point(row["end_longitude"], row["end_latitude"]), axis=1
        )
        self.trips_origins = gpd.GeoDataFrame(self.trips_origins)
        self.trips_origins.crs = "epsg:4326"
        self.trips_destinations = gpd.GeoDataFrame(self.trips_destinations)
        self.trips_destinations.crs = "epsg:4326"