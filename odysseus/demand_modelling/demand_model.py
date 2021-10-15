import os
import pickle
import datetime

from sklearn.neighbors import KernelDensity

from odysseus.utils.geospatial_utils import *

from odysseus.utils.time_utils import *


class DemandModel:

    def __init__(self, city_name, demand_model_config, save_folder = "default_demand_model"):

        self.city_name = city_name
        self.demand_model_config = demand_model_config
        self.save_folder = save_folder

        self.data_source_id = demand_model_config["data_source_id"]
        self.kde_bw = self.demand_model_config["kde_bandwidth"]

        self.avg_request_rate, self.request_rates = self.get_requests_rates()
        self.trip_kdes = self.get_trip_kdes()
        self.hourly_ods = dict()

        self.max_out_flow = float('-inf')
        self.max_in_flow = float('-inf')
        self.avg_out_flows_train = self.get_avg_out_flows()
        self.avg_in_flows_train = self.get_avg_in_flows()

    def get_hourly_ods(self):

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

        return self.avg_request_rate, self.request_rates

    def get_trip_kdes(self):

        kde_columns = [
            "origin_i",
            "origin_j",
            "destination_i",
            "destination_j",
        ]
        self.trip_kdes = dict()
        for daytype, daytype_bookings_gdf in self.bookings_train.groupby("daytype"):
            self.trip_kdes[daytype] = {}
            for hour in range(24):
                slot_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
                if len(slot_df):
                    self.trip_kdes[daytype][hour] = KernelDensity(
                        bandwidth=self.kde_bw
                    ).fit(slot_df[kde_columns].dropna())
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

        self.grid_matrix.to_pickle(os.path.join(demand_model_path, "grid_matrix.pickle"))
        self.grid_matrix.to_csv(os.path.join(demand_model_path, "grid_matrix.csv"))
        self.grid.geometry.to_file(os.path.join(demand_model_path, "grid.dbf"))
        self.grid.to_pickle(os.path.join(demand_model_path, "grid.pickle"))
        self.grid.to_csv(os.path.join(demand_model_path, "grid.csv"))
        pd.DataFrame(self.neighbors_dict).to_pickle(os.path.join(demand_model_path, "neighbors_dict.pickle"))
        pd.DataFrame(self.neighbors_dict).to_csv(os.path.join(demand_model_path, "neighbors_dict.csv"))
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
