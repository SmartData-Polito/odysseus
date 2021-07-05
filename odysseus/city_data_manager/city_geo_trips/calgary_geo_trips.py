import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString

from odysseus.city_data_manager.city_data_source.trips_data_source.calgary_scooter_trips import CalgaryScooterTrips
from odysseus.city_data_manager.city_data_source.geo_data_source.calgary_hexagonal_grid import CalgaryHexagonalGrid
from odysseus.city_data_manager.city_geo_trips.city_geo_trips import CityGeoTrips
from odysseus.utils.geospatial_utils import get_random_point_from_shape


class CalgaryGeoTrips(CityGeoTrips):

    def __init__(self, city_name="Calgary", trips_data_source_id="city_open_data", year=2019, month=7):

        self.city_name = city_name
        super().__init__(self.city_name, trips_data_source_id, year, month)
        self.trips_ds_dict = {
            "city_open_data": CalgaryScooterTrips()
        }
        self.trips_df_norm = pd.DataFrame()

        self.hexagonal_grid_ds = CalgaryHexagonalGrid()
        self.hexagonal_grid_ds.load_raw()
        self.hexagonal_grid_ds.normalise()
        self.hexagonal_grid_gdf_norm = self.hexagonal_grid_ds.gdf_norm

    def get_trips_od_gdfs(self):

        self.trips_ds_dict[self.trips_data_source_id].load_raw()
        self.trips_ds_dict[self.trips_data_source_id].normalise(self.year, self.month)

        self.trips_df_norm = self.trips_ds_dict[self.trips_data_source_id].load_norm(
            self.year, self.month
        )

        self.trips_df_norm["trip_id"] = self.trips_df_norm.index

        self.trips_origins = gpd.GeoDataFrame(pd.merge(
            self.trips_df_norm,
            self.hexagonal_grid_gdf_norm,
            left_on="starting_grid_id", right_on="grid_id"
        ))
        self.trips_origins.geometry = self.trips_origins.geometry.apply(
            get_random_point_from_shape
        )
        self.trips_origins.crs = "epsg:4326"

        self.trips_destinations = gpd.GeoDataFrame(pd.merge(
            self.trips_df_norm,
            self.hexagonal_grid_gdf_norm,
            left_on="ending_grid_id", right_on="grid_id"
        ))
        self.trips_destinations.geometry = self.trips_destinations.geometry.apply(
            get_random_point_from_shape
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
                         LineString([row["origin_point"], row["destination_point"]])],
            axis=1, result_type="expand"
        )

        self.trips = self.trips.drop(["origin_point", "destination_point"], axis=1)
        self.trips = gpd.GeoDataFrame(self.trips)
        self.trips.crs = "epsg:4326"
