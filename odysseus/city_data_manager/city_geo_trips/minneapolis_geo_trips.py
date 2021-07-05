import pandas as pd
import geopandas as gpd
import shapely

from odysseus.city_data_manager.city_data_source.trips_data_source.minneapolis_scooter_trips import MinneapolisScooterTrips
from odysseus.city_data_manager.city_data_source.geo_data_source.minneapolis_centerlines import MinneapolisCenterlines
from odysseus.city_data_manager.city_data_source.geo_data_source.minneapolis_trails_bikes import MinneapolisTrailsBikes
from odysseus.city_data_manager.city_geo_trips.city_geo_trips import CityGeoTrips
from odysseus.utils.geospatial_utils import get_random_point_from_linestring


class MinneapolisGeoTrips(CityGeoTrips):

    def __init__(self, city_name="Minneapolis", trips_data_source_id="city_open_data", year=2019, month=7):

        self.city_name = city_name
        super().__init__(self.city_name, trips_data_source_id, year, month)
        self.trips_ds_dict = {
            "city_open_data": MinneapolisScooterTrips()
        }
        self.trips_df_norm = pd.DataFrame()

        self.trails_ds = MinneapolisTrailsBikes()
        self.trails_ds.normalise()
        self.trails_gdf_norm = self.trails_ds.gdf_norm

        self.centerlines_ds = MinneapolisCenterlines()
        self.centerlines_ds.normalise()
        self.centerlines_gdf_norm = self.centerlines_ds.gdf_norm

    def get_trips_od_gdfs(self):

        self.trips_ds_dict[self.trips_data_source_id].load_raw(self.year, self.month)
        self.trips_ds_dict[self.trips_data_source_id].normalise(self.year, self.month)

        self.trips_df_norm = self.trips_ds_dict[self.trips_data_source_id].load_norm(
            self.year, self.month
        )
        self.trips_df_norm["trip_id"] = self.trips_df_norm.index

        trips_origins_trails = self.trips_df_norm.loc[
            self.trips_df_norm.start_centerline_id.isin(
                self.trails_gdf_norm.trail_id
            )]
        trips_destinations_trails = self.trips_df_norm.loc[
            self.trips_df_norm.end_centerline_id.isin(
                self.trails_gdf_norm.trail_id
            )]
        trips_origins_centerlines_index = self.trips_df_norm.index.difference(
            trips_origins_trails
        )
        trips_destinations_centerlines_index = self.trips_df_norm.index.difference(
            trips_destinations_trails
        )
        self.trips_df_norm.start_centerline_id = self.trips_df_norm.start_centerline_id.astype(str)
        self.trips_df_norm.end_centerline_id = self.trips_df_norm.end_centerline_id.astype(str)

        trips_origins_centerlines = self.trips_df_norm.loc[trips_origins_centerlines_index]
        trips_origins_centerlines.start_centerline_id = trips_origins_centerlines.start_centerline_id.apply(
            lambda string: string.split(".")[0]
        )
        trips_destinations_centerlines = self.trips_df_norm.loc[trips_destinations_centerlines_index]
        trips_destinations_centerlines.end_centerline_id = trips_destinations_centerlines.end_centerline_id.apply(
            lambda string: string.split(".")[0]
        )

        trips_origins_centerlines = gpd.GeoDataFrame(pd.merge(
            trips_origins_centerlines,
            self.centerlines_gdf_norm,
            left_on="start_centerline_id", right_on="centerline_id"
        ))
        if len(trips_origins_trails):
            trips_origins_trails = gpd.GeoDataFrame(pd.merge(
                trips_origins_trails,
                self.trails_gdf_norm,
                left_on="start_centerline_id", right_on="trail_id"
            ))
        self.trips_origins = pd.concat([
            trips_origins_centerlines,
            # trips_origins_trails
        ], sort=False)
        self.trips_origins.geometry = self.trips_origins.geometry.apply(
            get_random_point_from_linestring
        )
        self.trips_origins.crs = "epsg:4326"

        trips_destinations_centerlines = gpd.GeoDataFrame(pd.merge(
            trips_destinations_centerlines,
            self.centerlines_gdf_norm,
            left_on="end_centerline_id", right_on="centerline_id"
        ))
        if len(trips_destinations_trails):
            trips_destinations_trails = gpd.GeoDataFrame(pd.merge(
                trips_destinations_trails,
                self.trails_gdf_norm,
                left_on="end_centerline_id", right_on="trail_id"
            ))
        self.trips_destinations = pd.concat([
            trips_destinations_centerlines,
            # trips_destinations_trails
        ], sort=False)
        self.trips_destinations.geometry = self.trips_destinations.geometry.apply(
            get_random_point_from_linestring
        )
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
                         shapely.geometry.LineString([row["origin_point"], row["destination_point"]])],
            axis=1, result_type="expand"
        )

        self.trips = self.trips.drop(["origin_point", "destination_point"], axis=1)
        self.trips = gpd.GeoDataFrame(self.trips)
        self.trips.crs = "epsg:4326"
