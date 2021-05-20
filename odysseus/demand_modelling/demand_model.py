import os
import pickle
import datetime

from sklearn.neighbors import KernelDensity

from odysseus.utils.geospatial_utils import *

from odysseus.demand_modelling.loader import Loader
from odysseus.utils.time_utils import *


def get_in_flow_count(trips_destinations):

    in_flow_count = trips_destinations[["zone_id", "year", "month", "day", "end_hour", "end_time"]].groupby(
        ["zone_id", "year", "month", "day", "end_hour"], as_index=False
    ).count().rename(columns={"end_time": "in_flow_count"})

    return in_flow_count


def get_out_flow_count(trips_origins):

    out_flow_count = trips_origins[["zone_id", "year", "month", "day", "start_hour", "start_time"]].groupby(
        ["zone_id", "year", "month", "day", "start_hour"], as_index=False
    ).count().rename(columns={"start_time": "out_flow_count"})

    return out_flow_count


class DemandModel:

    def __init__(self, city_name, demand_model_config,
                 start_year_train, start_month_train, end_year_train, end_month_train,
                 start_year_test, start_month_test, end_year_test, end_month_test, save_folder = "default_demand_model"):

        self.city_name = city_name
        self.demand_model_config = demand_model_config
        self.save_folder = save_folder


        self.data_source_id = demand_model_config["data_source_id"]

        self.kde_bw = self.demand_model_config["kde_bandwidth"]

        self.bin_side_length = self.demand_model_config["bin_side_length"]

        self.bookings_train = pd.DataFrame()
        self.trips_origins_train = pd.DataFrame()
        self.trips_destinations_train = pd.DataFrame()
        for year, month in month_year_iter(start_month_train, start_year_train, end_month_train, end_year_train):
            print("train", year, month)
            self.loader = Loader(self.city_name, self.data_source_id, year, month)
            bookings, origins, destinations = self.loader.read_data()
            self.bookings_train = pd.concat([self.bookings_train, bookings], ignore_index=True)
            self.trips_origins_train = pd.concat([
                self.trips_origins_train, origins
            ], ignore_index=True, sort=False)
            self.trips_destinations_train = pd.concat([
                self.trips_destinations_train, destinations
            ], ignore_index=True, sort=False)

        self.bookings_train["date"] = self.bookings_train.start_time.apply(lambda d: d.date())
        self.bookings_train["daytype"] = self.bookings_train.start_daytype
        self.bookings_train["city"] = self.city_name
        self.bookings_train["euclidean_distance"] = self.bookings_train.apply(
            lambda pp: haversine(pp["start_longitude"], pp["start_latitude"], pp["end_longitude"], pp["end_latitude"]),
            axis=1
        )

        self.bookings_train = self.get_input_bookings_filtered(self.bookings_train).dropna()

        self.bookings_test = pd.DataFrame()
        self.trips_origins_test = pd.DataFrame()
        self.trips_destinations_test = pd.DataFrame()
        for year, month in month_year_iter(start_month_test, start_year_test, end_month_test, end_year_test):
            print("test", year, month)
            self.loader = Loader(self.city_name, self.data_source_id, year, month)
            bookings, origins, destinations = self.loader.read_data()
            self.bookings_test = pd.concat([self.bookings_test, bookings], ignore_index=True)
            self.trips_origins_test = pd.concat([
                self.trips_origins_test, origins
            ], ignore_index=True, sort=False)
            self.trips_destinations_test = pd.concat([
                self.trips_destinations_test, destinations
            ], ignore_index=True, sort=False)

        self.bookings_test["date"] = self.bookings_test.start_time.apply(lambda d: d.date())
        self.bookings_test["daytype"] = self.bookings_test.start_daytype
        self.bookings_test["city"] = self.city_name
        self.bookings_test["euclidean_distance"] = self.bookings_test.apply(
            lambda pp: haversine(pp["start_longitude"], pp["start_latitude"], pp["end_longitude"], pp["end_latitude"]),
            axis=1
        )

        self.bookings_test = self.get_input_bookings_filtered(self.bookings_test).dropna()

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

        print(self.grid.zone_id.values)
        print(self.grid_matrix.values.T.flatten())

        self.valid_zones = self.get_valid_zones()
        self.zones_valid_zones_distances = self.grid.centroid.apply(
            lambda x: self.grid.loc[self.valid_zones].centroid.distance(x)
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
        self.request_rates = self.get_requests_rates()
        self.get_grid_indexes()
        self.trip_kdes = self.get_trip_kdes()

        self.max_out_flow = float('-inf')
        self.max_in_flow = float('-inf')
        self.avg_out_flows_train = self.get_avg_out_flows()
        self.avg_in_flows_train = self.get_avg_in_flows()



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

        print(bookings[["euclidean_distance", "driving_distance", "duration", "avg_speed_kmh"]].describe())

        if self.city_name in [
            "Minneapolis", "Louisville", "Austin", "Norfolk", "Kansas City", "Chicago", "Calgary"
        ] or self.data_source_id in ["citi_bike"]:
            bookings = bookings[bookings.avg_speed_kmh < 30]
            bookings = bookings[(
                                                              bookings.duration > 60
                ) & (
                                                              bookings.duration < 60 * 60
                ) & (
                                                              bookings.euclidean_distance > 200
                )
                                                      ]
        elif self.data_source_id in ["big_data_db"]:
            bookings = bookings[bookings.avg_speed_kmh < 120]
            bookings = bookings[
                (bookings.duration > 3 * 60) & (
                        bookings.duration < 60 * 60
                ) & (
                        bookings.euclidean_distance > 500
                )
                ]

        print(bookings[["driving_distance", "duration", "avg_speed_kmh"]].describe())

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

    def get_neighbors_dicts(self):

        self.neighbors_dict = {}
        for i in self.grid_matrix.index:
            for j in self.grid_matrix.columns:
                zone = self.grid_matrix.iloc[i, j]
                i_low = i-1 if i-1 >= 0 else 0
                i_up = i+1 if i+1 < len(self.grid_matrix.index) else len(self.grid_matrix.index) - 1
                j_low = j-1 if j-1 >= 0 else 0
                j_up = j+1 if j+1 < len(self.grid_matrix.columns) else len(self.grid_matrix.columns) - 1
                iii = 0
                self.neighbors_dict[int(zone)] = {}
                for ii in range(i_low, i_up+1):
                    for jj in range(j_low, j_up+1):
                        if ii != i or jj != j and self.grid_matrix.iloc[ii, jj] in self.grid.index:
                            self.neighbors_dict[int(zone)].update({iii: self.grid_matrix.iloc[ii, jj]})
                            iii += 1
        return self.neighbors_dict

    def get_hourly_ods(self):

        self.hourly_ods = {}

        for hour, hour_df in self.bookings_train.groupby("hour"):
            self.hourly_ods[hour] = pd.DataFrame(
                index=self.grid.index,
                columns=self.grid.index
            )
            hourly_od = pd.pivot_table(
                hour_df,
                values="start_time",
                index="origin_id",
                columns="destination_id",
                aggfunc=len,
                fill_value=0
            )
            self.hourly_ods[hour].loc[hourly_od.index, hourly_od.columns] = hourly_od
            self.hourly_ods[hour].fillna(0, inplace=True)

    def get_requests_rates(self):

        self.request_rates = {}

        for daytype, daytype_bookings_gdf in self.bookings_train.groupby("daytype"):
            self.request_rates[daytype] = {}
            for hour in range(24):
                hour_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
                self.request_rates[daytype][hour] = hour_df.city.count() / (
                    len(daytype_bookings_gdf.date.unique())
                ) / 3600
            for hour in range(24):
                hour_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
                if len(hour_df) == 0 or self.request_rates[daytype][hour] == 0:
                    rates = pd.Series(self.request_rates[daytype])
                    self.request_rates[daytype][hour] = rates[rates > 0].min()

        self.avg_request_rate = pd.DataFrame(self.request_rates.values()).mean().mean()

        return self.request_rates

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
        for zone in self.valid_zones:
            self.bookings_test.loc[self.bookings_test.origin_id == zone, "origin_i"] = zone_coords_dict[zone][0]
            self.bookings_test.loc[self.bookings_test.origin_id == zone, "origin_j"] = zone_coords_dict[zone][1]
            self.bookings_test.loc[self.bookings_test.destination_id == zone, "destination_i"] = zone_coords_dict[zone][0]
            self.bookings_test.loc[self.bookings_test.destination_id == zone, "destination_j"] = zone_coords_dict[zone][1]

    def get_trip_kdes(self):
        self.trip_kdes = {}
        self.kde_columns = [
            "origin_i",
            "origin_j",
            "destination_i",
            "destination_j",
        ]

        for daytype, daytype_bookings_gdf in self.bookings_train.groupby("daytype"):
            self.trip_kdes[daytype] = {}
            for hour in range(24):
                slot_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
                if len(slot_df):
                    self.trip_kdes[daytype][hour] = KernelDensity(
                        bandwidth=self.kde_bw
                    ).fit(slot_df[self.kde_columns].dropna())
            hours_list = list(range(7, 24)) + list(range(7))
            for hour in hours_list:
                slot_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
                if len(slot_df) == 0:
                    rates = pd.Series(self.request_rates[daytype])
                    min_evaluable_rate = rates.idxmin()
                    while min_evaluable_rate not in self.trip_kdes[daytype].keys():
                        rates = rates.drop(min_evaluable_rate)
                        min_evaluable_rate = rates.idxmin()
                    self.trip_kdes[daytype][hour] = self.trip_kdes[daytype][min_evaluable_rate]

        return self.trip_kdes

    def get_avg_out_flows(self):
        self.avg_out_flows_train = {}
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
        self.avg_in_flows_train = {}
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

        demand_model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "demand_modelling",
            "demand_models",
            self.demand_model_config["city"],
            self.save_folder
        )

        with open(os.path.join(demand_model_path, "city_obj.pickle"), "wb") as f:
            pickle.dump(self, f)

        self.grid_matrix.to_pickle(
            os.path.join(demand_model_path, "grid_matrix.pickle")
        )
        self.grid_matrix.to_csv(
            os.path.join(demand_model_path, "grid_matrix.csv")
        )
        self.grid.geometry.to_file(
            os.path.join(demand_model_path, "grid.dbf")
        )
        self.grid.to_pickle(
            os.path.join(demand_model_path, "grid.pickle")
        )
        self.grid.to_csv(
            os.path.join(demand_model_path, "grid.csv")
        )
        pd.DataFrame(self.neighbors_dict).to_pickle(
            os.path.join(demand_model_path, "neighbors_dict.pickle")
        )
        pd.DataFrame(self.neighbors_dict).to_csv(
            os.path.join(demand_model_path, "neighbors_dict.csv")
        )
        self.bookings_train.to_csv(os.path.join(demand_model_path, "bookings_train.csv"))
        self.bookings_train.to_pickle(os.path.join(demand_model_path, "bookings_train.pickle"))
        self.bookings_test.to_csv(os.path.join(demand_model_path, "bookings_test.csv"))
        self.bookings_test.to_pickle(os.path.join(demand_model_path, "bookings_test.pickle"))
        self.closest_valid_zone.to_csv(os.path.join(demand_model_path, "closest_valid_zone.csv"))
        self.closest_valid_zone.to_pickle(os.path.join(demand_model_path, "closest_valid_zone.pickle"))

        with open(os.path.join(demand_model_path, "request_rates.pickle"), "wb") as f:
            pickle.dump(self.request_rates, f)
        with open(os.path.join(demand_model_path, "trip_kdes.pickle"), "wb") as f:
            pickle.dump(self.trip_kdes, f)
        with open(os.path.join(demand_model_path, "valid_zones.pickle"), "wb") as f:
            pickle.dump(self.valid_zones, f)
        with open(os.path.join(demand_model_path, "avg_out_flows_train.pickle"), "wb") as f:
            pickle.dump(self.avg_out_flows_train, f)
        with open(os.path.join(demand_model_path, "avg_in_flows_train.pickle"), "wb") as f:
            pickle.dump(self.avg_in_flows_train, f)

        integers_dict = {
            "avg_request_rate": self.avg_request_rate,
            "n_vehicles_original": self.n_vehicles_original,
            "avg_speed_mean": self.avg_speed_mean,
            "avg_speed_std": self.avg_speed_std,
            "avg_speed_kmh_mean": self.avg_speed_kmh_mean,
            "avg_speed_kmh_std": self.avg_speed_kmh_std,
            "max_driving_distance": self.max_driving_distance,
            "max_in_flow": self.max_in_flow,
            "max_out_flow": self.max_out_flow,
        }
        print(integers_dict)
        with open(os.path.join(demand_model_path, "integers_dict.pickle"), "wb") as f:
            pickle.dump(integers_dict, f)



    def save_in_flow_count(self):

        demand_model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "demand_modelling",
            "demand_models",
            self.demand_model_config["city"],
            self.save_folder
        )

        in_flow_count_train = get_in_flow_count(self.trips_destinations_train)
        in_flow_count_test = get_in_flow_count(self.trips_destinations_test)
        in_flow_count = pd.concat([in_flow_count_train, in_flow_count_test], axis=0, ignore_index=True)

        print(in_flow_count.shape)

        in_flow_count.sort_values(["year", "month", "day"]).reset_index(drop=True).rename(
            columns={"end_hour": "hour"}
        ).to_csv(os.path.join(demand_model_path, "in_flow_count.csv"))

    def save_out_flow_count(self):

        demand_model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "demand_modelling",
            "demand_models",
            self.demand_model_config["city"],
            self.save_folder
        )

        out_flow_count_train = get_out_flow_count(self.trips_origins_train)
        out_flow_count_test = get_out_flow_count(self.trips_origins_test)
        out_flow_count = pd.concat([out_flow_count_train, out_flow_count_test], axis=0, ignore_index=True)

        print(out_flow_count.shape)

        out_flow_count.sort_values(["year", "month", "day"]).reset_index(drop=True).rename(
            columns={"start_hour": "hour"}
        ).to_csv(os.path.join(demand_model_path, "out_flow_count.csv"))
