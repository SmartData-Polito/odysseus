import json
import os
import pickle

import pytz

import shapely

from odysseus.utils.time_utils import *
from odysseus.utils.geospatial_utils import *
from odysseus.path_config.path_config import *

from odysseus.city_scenario.abstract_city_scenario import AbstractCityScenario


class CityScenarioFromOD(AbstractCityScenario):

    def __init__(
            self, dummy_city_name, dummy_data_source_id, city_scenario_config=None
    ):

        super(CityScenarioFromOD, self).__init__(dummy_city_name, dummy_data_source_id)
        if city_scenario_config:
            self.city_scenario_config = city_scenario_config
            self.folder_name = self.city_scenario_config["folder_name"]

        self.city_scenario_path = os.path.join(
            city_scenarios_path,
            dummy_city_name,
            self.folder_name
        )

        self.bin_side_length = city_scenario_config["bin_side_length"]
        self.bookings_train = pd.DataFrame()
        self.bookings_test = pd.DataFrame()
        self.trips_origins_train = pd.DataFrame()
        self.trips_destinations_train = pd.DataFrame()
        self.trips_origins_test = pd.DataFrame()
        self.trips_destinations_test = pd.DataFrame()

        self.norm_od_matrices_path = os.path.join(
            root_data_path, self.city_name, "norm", "od_matrices", self.data_source_id
        )

        with open(os.path.join(self.norm_od_matrices_path, "grid_config.json"), "r") as f:
            self.grid_config = json.load(f)

        with open(os.path.join(self.norm_od_matrices_path, "week_config.json"), "r") as f:
            self.week_config = json.load(f)

        self.od_matrices = dict()
        for week_slot in self.week_config["week_slots"].keys():
            self.od_matrices[week_slot] = dict()
            for day_slot in self.week_config["day_slots"][week_slot]:
                self.od_matrices[week_slot][day_slot] = pd.read_csv(
                    os.path.join(
                        self.norm_od_matrices_path,
                        "_".join([week_slot, day_slot])
                    ) + ".csv", index_col=0
                )

        self.init_train_test()
        self.create_squared_city_grid(
            self.grid_config["n_cols"],
            self.grid_config["n_rows"],
            self.bin_side_length
        )

    def init_train_test(self):

        self.bookings_train = pd.read_csv(os.path.join(
            root_data_path, self.city_name, "norm", "trips", self.data_source_id, "bookings_train.csv"
        ))
        self.bookings_train.start_time = pd.to_datetime(self.bookings_train.start_time, utc=True)
        self.bookings_train.end_time = pd.to_datetime(self.bookings_train.end_time, utc=True)
        self.bookings_train = get_time_group_columns(self.bookings_train)

        valid_zones_train = set(self.bookings_train.origin_id.values).union(set(self.bookings_train.destination_id.values))

        self.bookings_test = pd.read_csv(os.path.join(
            root_data_path, self.city_name, "norm", "trips", self.data_source_id, "bookings_test.csv"
        ))
        self.bookings_test.start_time = pd.to_datetime(self.bookings_test.start_time, utc=True)
        self.bookings_test.end_time = pd.to_datetime(self.bookings_test.end_time, utc=True)
        self.bookings_test = get_time_group_columns(self.bookings_test)
        valid_zones_test = set(self.bookings_test.origin_id.values).union(set(self.bookings_test.destination_id.values))

        self.valid_zones = list(valid_zones_train.intersection(valid_zones_test))

        self.tz = pytz.timezone("Europe/London")

        self.year_energy_mix = self.bookings_test.start_time.apply(lambda d: d.year).values[0]

    def create_squared_city_grid(self, n_zones_x, n_zones_y, bin_side_length):

        self.bin_side_length = bin_side_length

        total_bounds = (
            0, 0, n_zones_x * bin_side_length, n_zones_y * bin_side_length
        )
        print(total_bounds)

        self.grid = get_city_grid_as_gdf(total_bounds, bin_side_length, "dummy_crs")

        self.grid["centroid_x"] = self.grid.loc[:, "geometry"].centroid.x
        self.grid["centroid_y"] = self.grid.loc[:, "geometry"].centroid.y
        self.grid_crs = self.grid.crs

        self.grid_matrix = get_city_grid_as_matrix(total_bounds, bin_side_length, "dummy_crs")

        print(self.grid)
        print(self.grid_matrix)

        self.bookings_train["origin_id"] = self.bookings_train[["origin_i", "origin_j"]].apply(
            lambda s: self.grid_matrix.loc[s[0], s[1]], axis=1
        )
        self.bookings_train["destination_id"] = self.bookings_train[["destination_i", "destination_j"]].apply(
            lambda s: self.grid_matrix.loc[s[0], s[1]], axis=1
        )
        self.bookings_train["start_longitude"] = self.bookings_train.origin_id.apply(
            lambda zone_id: self.grid.loc[zone_id].geometry.centroid.x
        )
        self.bookings_train["start_latitude"] = self.bookings_train.origin_id.apply(
            lambda zone_id: self.grid.loc[zone_id].geometry.centroid.y
        )
        self.bookings_train["end_longitude"] = self.bookings_train.destination_id.apply(
            lambda zone_id: self.grid.loc[zone_id].geometry.centroid.x
        )
        self.bookings_train["end_latitude"] = self.bookings_train.destination_id.apply(
            lambda zone_id: self.grid.loc[zone_id].geometry.centroid.y
        )

        self.bookings_test["origin_id"] = self.bookings_test[["origin_i", "origin_j"]].apply(
            lambda s: self.grid_matrix.loc[s[0], s[1]], axis=1
        )
        self.bookings_test["destination_id"] = self.bookings_test[["destination_i", "destination_j"]].apply(
            lambda s: self.grid_matrix.loc[s[0], s[1]], axis=1
        )
        self.bookings_test["start_longitude"] = self.bookings_test.origin_id.apply(
            lambda zone_id: self.grid.loc[zone_id].geometry.centroid.x
        )
        self.bookings_test["start_latitude"] = self.bookings_test.origin_id.apply(
            lambda zone_id: self.grid.loc[zone_id].geometry.centroid.y
        )
        self.bookings_test["end_longitude"] = self.bookings_test.destination_id.apply(
            lambda zone_id: self.grid.loc[zone_id].geometry.centroid.x
        )
        self.bookings_test["end_latitude"] = self.bookings_test.destination_id.apply(
            lambda zone_id: self.grid.loc[zone_id].geometry.centroid.y
        )

        self.trips_origins_train = self.bookings_train.copy()
        self.trips_destinations_train = self.bookings_train.copy()
        self.trips_origins_train["geometry"] = self.trips_origins_train.apply(
            lambda row: shapely.geometry.Point(row["start_longitude"], row["start_latitude"]), axis=1
        )
        self.trips_origins_train = gpd.GeoDataFrame(self.trips_origins_train)
        self.trips_origins_train.crs = "epsg:3857"

        self.trips_destinations_train["geometry"] = self.trips_destinations_train.apply(
            lambda row: shapely.geometry.Point(row["end_longitude"], row["end_latitude"]), axis=1
        )
        self.trips_destinations_train = gpd.GeoDataFrame(self.trips_destinations_train)
        self.trips_destinations_train.crs = "epsg:3857"

        self.trips_origins_test = self.bookings_test.copy()
        self.trips_destinations_test = self.bookings_test.copy()
        self.trips_origins_test["geometry"] = self.trips_origins_test.apply(
            lambda row: shapely.geometry.Point(row["start_longitude"], row["start_latitude"]), axis=1
        )
        self.trips_origins_test = gpd.GeoDataFrame(self.trips_origins_test)
        self.trips_origins_test.crs = "epsg:3857"

        self.trips_destinations_test["geometry"] = self.trips_destinations_test.apply(
            lambda row: shapely.geometry.Point(row["end_longitude"], row["end_latitude"]), axis=1
        )
        self.trips_destinations_test = gpd.GeoDataFrame(self.trips_destinations_test)
        self.trips_destinations_test.crs = "epsg:3857"

        self.map_zones_on_trips(self.grid)

        self.distance_matrix = self.grid.loc[self.valid_zones].centroid.apply(
            lambda x: self.grid.loc[self.valid_zones].centroid.distance(x).sort_values()
        ) * 111139
        self.closest_zones = dict()
        for zone_id in self.valid_zones:
            self.closest_zones[zone_id] = list(
                self.distance_matrix[self.distance_matrix > 0].loc[zone_id].sort_values().dropna().index.values
            )

        self.bookings_train["euclidean_distance"] = self.bookings_train[
            ["origin_id", "destination_id"]
        ].apply(
            lambda s: get_od_distance(
                grid_centroids=self.grid, origin_id=s[0], destination_id=s[1], crs=self.grid_crs
            ), axis=1
        )
        self.bookings_train = self.get_input_bookings_filtered(self.bookings_train).dropna()

        self.bookings_test["euclidean_distance"] = self.bookings_test[
            ["origin_id", "destination_id"]
        ].apply(
            lambda s: get_od_distance(
                grid_centroids=self.grid, origin_id=s[0], destination_id=s[1], crs=self.grid_crs
            ), axis=1
        )
        self.bookings_test = self.get_input_bookings_filtered(self.bookings_test).dropna()

    def save_virtual_od_results(self):

        os.makedirs(self.city_scenario_path, exist_ok=True)

        print(self.od_matrices)

        with open(os.path.join(self.city_scenario_path, "week_config.json"), "w") as f:
            json.dump(self.week_config, f)

        with open(os.path.join(self.city_scenario_path, "od_matrices.pickle"), "wb") as f:
            pickle.dump(self.od_matrices, f)
