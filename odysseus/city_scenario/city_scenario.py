import os
import json
import pickle
import datetime

import pandas as pd

from odysseus.city_scenario.city_data_loader import CityDataLoader
from odysseus.utils.time_utils import *
from odysseus.utils.geospatial_utils import *
from odysseus.path_config.path_config import *


class CityScenario:

    def __init__(self, city, from_file=False, city_scenario_config=None, in_folder_name=None):

        self.city_name = city

        if from_file and in_folder_name:
            self.folder_name = in_folder_name
        elif city_scenario_config:
            self.city_scenario_config = city_scenario_config
            self.folder_name = self.city_scenario_config["folder_name"]
        else:
            raise IOError("Wrong arguments for CityScenario!")

        self.city_scenario_path = os.path.join(
            city_scenarios_path,
            city,
            self.folder_name
        )
        if from_file and in_folder_name:
            self.read_config_from_folder_name()

        self.data_source_id = self.city_scenario_config["data_source_id"]
        self.bin_side_length = int(self.city_scenario_config["bin_side_length"])

        self.loader = CityDataLoader(self.city_name, self.data_source_id)

        self.bookings_train = pd.DataFrame()
        self.trips_origins_train = pd.DataFrame()
        self.trips_destinations_train = pd.DataFrame()

        self.bookings_test = pd.DataFrame()
        self.trips_origins_test = pd.DataFrame()
        self.trips_destinations_test = pd.DataFrame()

        self.integers_dict = dict()
        self.avg_speed_mean = -1
        self.avg_speed_std = -1
        self.avg_speed_kmh_mean = -1
        self.avg_speed_kmh_std = -1
        self.max_driving_distance = -1
        self.n_vehicles_original = -1

        self.grid = pd.DataFrame()
        self.grid_matrix = pd.DataFrame()

        self.valid_zones = None
        self.zones_valid_zones_distances = None
        self.closest_valid_zone = None

        self.neighbors_dict = dict()
        self.max_out_flow = float('-inf')
        self.max_in_flow = float('-inf')
        self.avg_out_flows_train = dict()
        self.avg_in_flows_train = dict()

        self.energy_mix = None

    def create_city_scenario(
            self, start_year_train, start_month_train, end_year_train, end_month_train,
                 start_year_test, start_month_test, end_year_test, end_month_test
    ):

        self.bookings_train, self.trips_origins_train, self.trips_destinations_train = \
            self.loader.read_year_month_range_data(
                start_month_train, start_year_train, end_month_train, end_year_train
            )
        self.bookings_train = self.get_input_bookings_filtered(self.bookings_train).dropna()

        self.bookings_test, self.trips_origins_test, self.trips_destinations_test = \
            self.loader.read_year_month_range_data(
                start_month_test, start_year_test, end_month_test, end_year_test
            )
        self.bookings_train = self.get_input_bookings_filtered(self.bookings_test).dropna()

        self.avg_speed_mean = self.bookings_train.avg_speed.mean()
        self.avg_speed_std = self.bookings_train.avg_speed.std()
        self.avg_speed_kmh_mean = self.bookings_train.avg_speed_kmh.mean()
        self.avg_speed_kmh_std = self.bookings_train.avg_speed_kmh.std()
        self.max_driving_distance = self.bookings_train.driving_distance.max()

        self.grid = get_city_grid_as_gdf(
            (
                min(self.trips_origins_train.start_longitude.min(), self.trips_destinations_train.end_longitude.min(),
                    self.trips_origins_test.start_longitude.min(), self.trips_destinations_test.end_longitude.min()),
                min(self.trips_origins_train.start_latitude.min(), self.trips_destinations_train.end_latitude.min(),
                    self.trips_origins_test.start_latitude.min(), self.trips_destinations_test.end_latitude.min()),
                max(self.trips_origins_train.start_longitude.max(), self.trips_destinations_train.end_longitude.max(),
                    self.trips_origins_test.start_longitude.max(), self.trips_destinations_test.end_longitude.max()),
                max(self.trips_origins_train.start_latitude.max(), self.trips_destinations_train.end_latitude.max(),
                    self.trips_origins_test.start_latitude.max(), self.trips_destinations_test.end_latitude.max())
            ),
            "epsg:4326",
            self.bin_side_length
        )
        self.grid_matrix = get_city_grid_as_matrix(
            (
                min(self.trips_origins_train.start_longitude.min(), self.trips_destinations_train.end_longitude.min(),
                    self.trips_origins_test.start_longitude.min(), self.trips_destinations_test.end_longitude.min()),
                min(self.trips_origins_train.start_latitude.min(), self.trips_destinations_train.end_latitude.min(),
                    self.trips_origins_test.start_latitude.min(), self.trips_destinations_test.end_latitude.min()),
                max(self.trips_origins_train.start_longitude.max(), self.trips_destinations_train.end_longitude.max(),
                    self.trips_origins_test.start_longitude.max(), self.trips_destinations_test.end_longitude.max()),
                max(self.trips_origins_train.start_latitude.max(), self.trips_destinations_train.end_latitude.max(),
                    self.trips_origins_test.start_latitude.max(), self.trips_destinations_test.end_latitude.max())
            ),
            self.bin_side_length
        )
        self.grid["zone_id"] = self.grid.index.values
        self.map_zones_on_trips(self.grid)

        self.valid_zones = self.get_valid_zones()
        self.zones_valid_zones_distances = self.grid.to_crs("epsg:3857").centroid.apply(
            lambda x: self.grid.to_crs("epsg:3857").loc[self.valid_zones].centroid.distance(x)
        )
        self.closest_valid_zone = self.zones_valid_zones_distances.idxmin(axis=1)
        self.grid = self.grid.loc[self.valid_zones]

        self.bookings_train = self.bookings_train.loc[
            (self.bookings_train.origin_id.isin(self.valid_zones)) & (
                self.bookings_train.destination_id.isin(self.valid_zones)
            )
        ]
        self.grid["origin_count"] = self.bookings_train.origin_id.value_counts()
        self.grid["destination_count"] = self.bookings_train.destination_id.value_counts()
        reqs_per_zone = self.bookings_train.origin_id.value_counts(
            normalize=False
        ).rename('zone_id')
        self.grid = self.grid.join(reqs_per_zone, how='left', on='zone_id', rsuffix='_origin_count')

        if 'plate' in self.bookings_train:
            self.n_vehicles_original = len(self.bookings_train.plate.unique())
        elif 'vehicle_id' in self.bookings_train:
            self.n_vehicles_original = len(self.bookings_train.vehicle_id.unique())
        else:
            self.n_vehicles_original = 100

        self.neighbors_dict = self.get_neighbors_dicts()
        self.get_grid_indexes()

        self.max_out_flow = float('-inf')
        self.max_in_flow = float('-inf')
        self.avg_out_flows_train = self.get_avg_out_flows()
        self.avg_in_flows_train = self.get_avg_in_flows()

        self.energy_mix = EnergyMix(self.city_name, start_year_test)

    def map_zones_on_trips(self, zones):

        self.trips_origins_train = gpd.sjoin(
            self.trips_origins_train,
            zones,
            how='left',
            op='intersects'
        )
        self.trips_destinations_train = gpd.sjoin(
            self.trips_destinations_train,
            zones,
            how='left',
            op='intersects'
        )
        self.trips_origins_test = gpd.sjoin(
            self.trips_origins_test,
            zones,
            how='left',
            op='intersects'
        )
        self.trips_destinations_test = gpd.sjoin(
            self.trips_destinations_test,
            zones,
            how='left',
            op='intersects'
        )
        self.bookings_train["origin_id"] = self.trips_origins_train.zone_id
        self.bookings_train["destination_id"] = self.trips_destinations_train.zone_id
        self.bookings_test["origin_id"] = self.trips_origins_test.zone_id
        self.bookings_test["destination_id"] = self.trips_destinations_test.zone_id

    def get_input_bookings_filtered(self, bookings):

        bookings = bookings.sort_values("start_time")

        if "driving_distance" not in bookings.columns:
            bookings["driving_distance"] = bookings.euclidean_distance * 1.4

        #bookings = get_time_group_columns(bookings)
        bookings["hour"] = bookings.start_hour
        bookings["daytype"] = bookings.start_daytype
        bookings["date"] = bookings.start_time.apply(lambda d: d.date())

        bookings["random_seconds_start"] = np.random.uniform(-900, 900, len(bookings))
        bookings.start_time = pd.to_datetime(
            bookings.start_time, utc=True
        ) + bookings.random_seconds_start.apply(
            lambda sec: datetime.timedelta(seconds=sec)
        )
        bookings["random_seconds_end"] = np.random.uniform(-900, 900, len(bookings))
        bookings["random_seconds_pos"] = np.random.uniform(0, 450, len(bookings))

        bookings.end_time = pd.to_datetime(
            bookings.end_time, utc=True
        ) + bookings.random_seconds_end.apply(
            lambda sec: datetime.timedelta(seconds=sec)
        )

        bookings["start_time"] = bookings["start_time"].dt.tz_convert(self.loader.tz)
        bookings["end_time"] = bookings["end_time"].dt.tz_convert(self.loader.tz)

        bookings = get_time_group_columns(bookings)
        bookings["hour"] = bookings.start_hour
        bookings["daytype"] = bookings.start_daytype
        bookings["date"] = bookings.start_time.apply(lambda d: d.date())

        bookings.loc[bookings.start_time > bookings.end_time, "end_time"] = bookings.loc[
            bookings.start_time > bookings.end_time, "start_time"
        ] + bookings.loc[bookings.start_time > bookings.end_time, "random_seconds_pos"].apply(
            lambda sec: datetime.timedelta(seconds=sec)
        )
        bookings.loc[:, "duration"] = (
                bookings.end_time - bookings.start_time
        ).apply(lambda x: x.total_seconds())

        bookings = bookings.sort_values("start_time")
        bookings.loc[:, "ia_timeout"] = (
                bookings.start_time - bookings.start_time.shift()
        ).apply(lambda x: x.total_seconds()).abs()
        bookings = bookings.loc[bookings.ia_timeout >= 0]

        bookings = bookings[bookings.duration > 0]
        bookings = bookings[bookings.driving_distance >= 0]
        bookings.loc[bookings.driving_distance == 0, "driving_distance"] = self.bin_side_length
        bookings["avg_speed"] = bookings["driving_distance"] / bookings["duration"]
        bookings["avg_speed_kmh"] = bookings.avg_speed * 3.6

        if self.city_name in [
            "Minneapolis", "Louisville", "Austin", "Norfolk", "Kansas City", "Chicago", "Calgary"
        ] or self.data_source_id in ["citi_bike"]:
            bookings = bookings[bookings.avg_speed_kmh < 30]
            bookings = bookings[
                (bookings.duration > 60) & (
                    bookings.duration < 60 * 60
                ) & (bookings.euclidean_distance > 200)
            ]

        elif self.data_source_id in ["big_data_db"]:
            bookings = bookings[bookings.avg_speed_kmh < 120]
            bookings = bookings[
                (bookings.duration > 3 * 60) & (
                    bookings.duration < 60 * 60
                ) & (bookings.euclidean_distance > 500)
            ]

        return bookings

    def get_valid_zones(self, count_threshold=0):

        # self.valid_zones = self.trips_origins_train.origin_id.value_counts().sort_values().tail(
        #     int(self.sim_general_conf["k_zones_factor"] * len(self.grid))
        # ).index

        origin_zones_count_train = self.bookings_train.origin_id.value_counts()
        dest_zones_count_train = self.bookings_train.destination_id.value_counts()
        origin_zones_count_test = self.bookings_test.origin_id.value_counts()
        dest_zones_count_test = self.bookings_test.destination_id.value_counts()

        valid_origin_zones_train = origin_zones_count_train[(origin_zones_count_train > count_threshold)]
        valid_dest_zones_train = dest_zones_count_train[(dest_zones_count_train > count_threshold)]
        valid_origin_zones_test = origin_zones_count_test[(origin_zones_count_test > count_threshold)]
        valid_dest_zones_test = dest_zones_count_test[(dest_zones_count_test > count_threshold)]

        valid_zones_train = valid_origin_zones_train.index.intersection(
            valid_dest_zones_train.index
        ).astype(int)

        valid_zones_test = valid_origin_zones_test.index.intersection(
            valid_dest_zones_test.index
        ).astype(int)

        self.valid_zones = valid_zones_train.intersection(valid_zones_test)

        return self.valid_zones

    def get_neighbors_dicts(self, max_n_hops=1):

        n_rows = len(self.grid_matrix.index)
        n_cols = len(self.grid_matrix.columns)
        for current_max_n_hops in range(1, max_n_hops+1):
            for i in self.grid_matrix.index:
                for j in self.grid_matrix.columns:
                    zone = self.grid_matrix.iloc[i, j]
                    i_up = i-max_n_hops if i-max_n_hops >= 0 else 0
                    i_low = i+max_n_hops if i+max_n_hops < len(self.grid_matrix.index) else n_rows - 1
                    j_left = j-max_n_hops if j-max_n_hops >= 0 else 0
                    j_right = j+max_n_hops if j+max_n_hops < len(self.grid_matrix.columns) else n_cols - 1
                    self.neighbors_dict[int(zone)] = dict()
                    for ii in range(i_up, i_low+1):
                        for jj in range(j_left, j_right+1):
                            if ii != i or jj != j and self.grid_matrix.iloc[ii, jj] in self.grid.index:
                                self.neighbors_dict[int(zone)].update(
                                    {len(self.neighbors_dict[int(zone)].keys()): self.grid_matrix.iloc[ii, jj]}
                                )
        return self.neighbors_dict

    def get_grid_indexes(self):
        zone_coords_dict = {}
        for j in self.grid_matrix.columns:
            for i in self.grid_matrix.index:
                zone_coords_dict[self.grid_matrix.iloc[i, j]] = (i, j)

        for zone in self.valid_zones:
            self.bookings_train.loc[self.bookings_train.origin_id == zone, "origin_i"] = zone_coords_dict[zone][0]
            self.bookings_train.loc[self.bookings_train.origin_id == zone, "origin_j"] = zone_coords_dict[zone][1]
            self.bookings_train.loc[self.bookings_train.destination_id == zone, "destination_i"] = zone_coords_dict[zone][0]
            self.bookings_train.loc[self.bookings_train.destination_id == zone, "destination_j"] = zone_coords_dict[zone][1]
            self.bookings_test.loc[self.bookings_test.origin_id == zone, "origin_i"] = zone_coords_dict[zone][0]
            self.bookings_test.loc[self.bookings_test.origin_id == zone, "origin_j"] = zone_coords_dict[zone][1]
            self.bookings_test.loc[self.bookings_test.destination_id == zone, "destination_i"] = zone_coords_dict[zone][0]
            self.bookings_test.loc[self.bookings_test.destination_id == zone, "destination_j"] = zone_coords_dict[zone][1]

    def get_avg_out_flows(self):
        for daytype, daytype_df in self.trips_origins_train.groupby("start_daytype"):
            self.avg_out_flows_train[daytype] = {}
            for hour, hour_df in daytype_df.groupby("start_hour"):
                self.avg_out_flows_train[daytype][hour] = {}
                for zone, zone_df in hour_df.groupby("zone_id"):
                    if zone in self.valid_zones:
                        out_flows = zone_df[["day", "start_time"]].groupby("day").count()
                        self.avg_out_flows_train[daytype][hour][zone] = out_flows.mean()[0]
                        out_flows_max = out_flows.max()[0]
                        if out_flows_max > self.max_out_flow:
                            self.max_out_flow = out_flows_max

        for daytype in ["weekday", "weekend"]:
            for hour in range(24):
                for zone in self.valid_zones:
                    if daytype not in self.avg_out_flows_train:
                        self.avg_out_flows_train[daytype] = {}
                    if hour not in self.avg_out_flows_train[daytype]:
                        self.avg_out_flows_train[daytype][hour] = {}
                    if zone not in self.avg_out_flows_train[daytype][hour]:
                        self.avg_out_flows_train[daytype][hour][zone] = 0

        return self.avg_out_flows_train

    def get_avg_in_flows(self):
        for daytype, daytype_df in self.trips_destinations_train.groupby("end_daytype"):
            self.avg_in_flows_train[daytype] = {}
            for hour, hour_df in daytype_df.groupby("end_hour"):
                self.avg_in_flows_train[daytype][hour] = {}
                for zone, zone_df in hour_df.groupby("zone_id"):
                    if zone in self.valid_zones:
                        in_flows = zone_df[["day", "end_time"]].groupby("day").count()
                        self.avg_in_flows_train[daytype][hour][zone] = in_flows.mean()[0]
                        in_flows_max = in_flows.max()[0]
                        if in_flows_max > self.max_in_flow:
                            self.max_in_flow = in_flows_max

        for daytype in ["weekday", "weekend"]:
            for hour in range(24):
                for zone in self.valid_zones:
                    if daytype not in self.avg_in_flows_train:
                        self.avg_in_flows_train[daytype] = {}
                    if hour not in self.avg_in_flows_train[daytype]:
                        self.avg_in_flows_train[daytype][hour] = {}
                    if zone not in self.avg_in_flows_train[daytype][hour]:
                        self.avg_in_flows_train[daytype][hour][zone] = 0

        return self.avg_in_flows_train

    def save_results(self):

        os.makedirs(self.city_scenario_path, exist_ok=True)

        with open(os.path.join(self.city_scenario_path, "city_scenario_config.json"), "w") as f:
            json.dump(self.city_scenario_config, f)

        with open(os.path.join(self.city_scenario_path, "city_obj.pickle"), "wb") as f:
            pickle.dump(self, f)

        self.grid_matrix.to_pickle(os.path.join(self.city_scenario_path, "grid_matrix.pickle"))
        self.grid_matrix.to_csv(os.path.join(self.city_scenario_path, "grid_matrix.csv"))
        self.grid.geometry.to_file(os.path.join(self.city_scenario_path, "grid.dbf"))
        self.grid.to_pickle(os.path.join(self.city_scenario_path, "grid.pickle"))
        self.grid.to_csv(os.path.join(self.city_scenario_path, "grid.csv"))
        pd.DataFrame(self.neighbors_dict).to_pickle(os.path.join(self.city_scenario_path, "neighbors_dict.pickle"))
        pd.DataFrame(self.neighbors_dict).to_csv(os.path.join(self.city_scenario_path, "neighbors_dict.csv"))
        self.bookings_train.to_csv(os.path.join(self.city_scenario_path, "bookings_train.csv"))
        self.bookings_train.to_pickle(os.path.join(self.city_scenario_path, "bookings_train.pickle"))
        self.bookings_test.to_csv(os.path.join(self.city_scenario_path, "bookings_test.csv"))
        self.bookings_test.to_pickle(os.path.join(self.city_scenario_path, "bookings_test.pickle"))
        self.closest_valid_zone.to_csv(os.path.join(self.city_scenario_path, "closest_valid_zone.csv"))
        self.closest_valid_zone.to_pickle(os.path.join(self.city_scenario_path, "closest_valid_zone.pickle"))

        with open(os.path.join(self.city_scenario_path, "valid_zones.pickle"), "wb") as f:
            pickle.dump(self.valid_zones, f)
        with open(os.path.join(self.city_scenario_path, "avg_out_flows_train.pickle"), "wb") as f:
            pickle.dump(self.avg_out_flows_train, f)
        with open(os.path.join(self.city_scenario_path, "avg_in_flows_train.pickle"), "wb") as f:
            pickle.dump(self.avg_in_flows_train, f)

        integers_dict = {
            "n_vehicles_original": self.n_vehicles_original,
            "avg_speed_mean": self.avg_speed_mean,
            "avg_speed_std": self.avg_speed_std,
            "avg_speed_kmh_mean": self.avg_speed_kmh_mean,
            "avg_speed_kmh_std": self.avg_speed_kmh_std,
            "max_driving_distance": self.max_driving_distance,
            "max_in_flow": self.max_in_flow,
            "max_out_flow": self.max_out_flow,
        }
        with open(os.path.join(self.city_scenario_path, "integers_dict.pickle"), "wb") as f:
            pickle.dump(integers_dict, f)

        in_flow_count_train = get_in_flow_count(self.trips_destinations_train)
        in_flow_count_test = get_in_flow_count(self.trips_destinations_test)
        in_flow_count = pd.concat([in_flow_count_train, in_flow_count_test], axis=0, ignore_index=True)

        in_flow_count.sort_values(["year", "month", "day"]).reset_index(drop=True).rename(
            columns={"end_hour": "hour"}
        ).to_csv(os.path.join(self.city_scenario_path, "in_flow_count.csv"))

        out_flow_count_train = get_out_flow_count(self.trips_origins_train)
        out_flow_count_test = get_out_flow_count(self.trips_origins_test)
        out_flow_count = pd.concat([out_flow_count_train, out_flow_count_test], axis=0, ignore_index=True)

        out_flow_count.sort_values(["year", "month", "day"]).reset_index(drop=True).rename(
            columns={"start_hour": "hour"}
        ).to_csv(os.path.join(self.city_scenario_path, "out_flow_count.csv"))

    def read_config_from_folder_name(self):
        with open(os.path.join(self.city_scenario_path, "city_scenario_config.json"), "r") as f:
            self.city_scenario_config = json.load(f)

    def read_city_scenario_for_supply_model(self):

        assert os.path.exists(self.city_scenario_path)

        self.grid = pickle.Unpickler(open(os.path.join(self.city_scenario_path, "grid.pickle"), "rb")).load()
        self.valid_zones = pickle.Unpickler(open(os.path.join(self.city_scenario_path, "valid_zones.pickle"), "rb")).load()
        self.neighbors_dict = pickle.Unpickler(open(os.path.join(self.city_scenario_path, "neighbors_dict.pickle"), "rb")).load()
        self.integers_dict = pickle.Unpickler(open(os.path.join(self.city_scenario_path, "integers_dict.pickle"), "rb")).load()

    def read_city_scenario_for_demand_model(self):

        assert os.path.exists(self.city_scenario_path)

        self.grid = pickle.Unpickler(open(os.path.join(self.city_scenario_path, "grid.pickle"), "rb")).load()
        self.bookings_train = pickle.Unpickler(open(os.path.join(self.city_scenario_path, "bookings_train.pickle"), "rb")).load()
