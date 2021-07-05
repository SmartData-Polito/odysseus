import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString

from odysseus.city_data_manager.city_data_source.trips_data_source.chicago_scooter_trips import ChicagoScooterTrips
from odysseus.city_data_manager.city_data_source.geo_data_source.chicago_census_tracts import ChicagoCensusTracts
from odysseus.city_data_manager.city_data_source.geo_data_source.chicago_community_areas import ChicagoCommunityAreas
from odysseus.city_data_manager.city_geo_trips.city_geo_trips import CityGeoTrips
from odysseus.utils.geospatial_utils import get_random_point_from_shape


class ChicagoGeoTrips(CityGeoTrips):

    def __init__(self, city_name="Chicago", trips_data_source_id="city_open_data", year=2019, month=7):

        self.city_name = city_name
        super().__init__(self.city_name, trips_data_source_id, year, month)
        self.trips_ds_dict = {
            "city_open_data": ChicagoScooterTrips()
        }
        self.trips_df_norm = pd.DataFrame()

        self.census_tracts_ds = ChicagoCensusTracts()
        self.census_tracts_ds.load_raw()
        self.census_tracts_ds.normalise()
        self.census_tracts_gdf_norm = self.census_tracts_ds.gdf_norm

        self.community_areas_ds = ChicagoCommunityAreas()
        self.community_areas_ds.load_raw()
        self.community_areas_ds.normalise()
        self.community_areas_gdf_norm = self.community_areas_ds.gdf_norm

    def get_trips_od_gdfs(self):

        self.trips_ds_dict[self.trips_data_source_id].load_raw()
        self.trips_ds_dict[self.trips_data_source_id].normalise(self.year, self.month)

        self.trips_df_norm = self.trips_ds_dict[self.trips_data_source_id].load_norm(
            self.year, self.month
        )

        self.trips_origins = pd.merge(
            self.trips_df_norm,
            self.community_areas_gdf_norm,
            left_on="start_community_area_number", right_on="community_area_number"
        )

        self.trips_origins = pd.merge(
            self.trips_origins,
            self.census_tracts_gdf_norm,
            left_on="start_census_tract", right_on="census_tract_id",
            how="left", suffixes=["_community_area", "_census_tract"]
        )

        self.trips_origins["geometry"] = self.trips_origins.apply(
            lambda row:
            get_random_point_from_shape(row["geometry_census_tract"]) if row["geometry_census_tract"]
            else get_random_point_from_shape(row["geometry_community_area"]),
            axis=1
        )

        self.trips_origins = self.trips_origins.drop([
            "geometry_community_area",
            "geometry_census_tract"
        ], axis=1)
        self.trips_origins = gpd.GeoDataFrame(self.trips_origins)
        self.trips_origins.crs = "epsg:4326"

        self.trips_destinations = pd.merge(
            self.trips_df_norm,
            self.community_areas_gdf_norm,
            left_on="end_community_area_number", right_on="community_area_number"
        )

        self.trips_destinations = pd.merge(
            self.trips_destinations,
            self.census_tracts_gdf_norm,
            left_on="end_census_tract", right_on="census_tract_id",
            how="left", suffixes=["_community_area", "_census_tract"]
        )

        self.trips_destinations["geometry"] = self.trips_destinations.apply(
            lambda row:
            get_random_point_from_shape(row["geometry_census_tract"]) if row["geometry_census_tract"]
            else get_random_point_from_shape(row["geometry_community_area"]),
            axis=1
        )

        self.trips_destinations = self.trips_destinations.drop([
            "geometry_community_area",
            "geometry_census_tract"
        ], axis=1)
        self.trips_destinations = gpd.GeoDataFrame(self.trips_destinations)
        self.trips_destinations.crs = "epsg:4326"

        self.trips = pd.merge(
            self.trips_df_norm,
            self.trips_origins[["trip_id", "geometry"]],
            on="trip_id"
        )
        self.trips = self.trips.rename(columns={"geometry": "origin_point"})

        self.trips = pd.merge(
            self.trips,
            self.trips_destinations[["trip_id", "geometry"]],
            on="trip_id"
        )
        self.trips = self.trips.rename(columns={"geometry": "destination_point"})

        self.trips[["start_latitude",
                    "start_longitude",
                    "end_latitude",
                    "end_longitude",
                    "geometry"]] = self.trips.apply(
            lambda row: [row["origin_point"].y,
                         row["origin_point"].x,
                         row["destination_point"].y,
                         row["destination_point"].x,
                         LineString([row["origin_point"], row["destination_point"]])],
            axis=1, result_type="expand"
        )

        self.trips = self.trips.drop(["origin_point", "destination_point"], axis=1)
        self.trips = gpd.GeoDataFrame(self.trips)
        self.trips.crs = "epsg:4326"
