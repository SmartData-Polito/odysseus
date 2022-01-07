import os
import json
import pickle

from sklearn.neighbors import KernelDensity

from odysseus.city_scenario.city_scenario import CityScenario

from odysseus.utils.bookings_utils import *


class DemandModel:

    def __init__(
            self,
            city_name,
            data_source_id,
            demand_model_config
    ):

        self.demand_model_config = demand_model_config

        self.city_name = city_name
        self.data_source_id = data_source_id

        self.city_scenario_folder = self.demand_model_config["city_scenario_folder"]
        self.demand_model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "demand_modelling",
            "city_demand_models",
            self.city_name,
            self.city_scenario_folder
        )

        self.city_scenario = CityScenario(
            city_name=self.city_name,
            data_source_id=self.data_source_id,
            read_config_from_file=True,
            in_folder_name=self.city_scenario_folder
        )
        self.city_scenario.read_city_scenario_for_demand_model()
        self.bookings_train = self.city_scenario.bookings_train
        self.grid = self.city_scenario.grid

        self.kde_bw = float(self.demand_model_config["kde_bandwidth"])

        self.avg_request_rate = -1
        self.request_rates = dict()
        self.trip_kdes = dict()
        self.od_matrices = dict()

        self.max_out_flow = float('-inf')
        self.max_in_flow = float('-inf')

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

        os.makedirs(self.demand_model_path, exist_ok=True)

        with open(os.path.join(self.demand_model_path, "demand_model_config.json"), "w") as f:
            json.dump(self.demand_model_config, f, sort_keys=True, indent=4)

        with open(os.path.join(self.demand_model_path, "request_rates.pickle"), "wb") as f:
            pickle.dump(self.request_rates, f)
        with open(os.path.join(self.demand_model_path, "request_rates.json"), "w") as f:
            json.dump(self.request_rates, f, sort_keys=True, indent=4)

        with open(os.path.join(self.demand_model_path, "trip_kdes.pickle"), "wb") as f:
            pickle.dump(self.trip_kdes, f)

        for daytype in self.od_matrices.keys():
            daytype_writer = pd.ExcelWriter(
                os.path.join(self.demand_model_path, "_".join([daytype, "od_matrices.xlsx"])),
            )
            for hour in range(24):
                self.od_matrices[daytype][hour].to_excel(
                    daytype_writer, sheet_name="_".join([daytype, str(hour)])
                )
            daytype_writer.save()

        with open(os.path.join(self.demand_model_path, "od_matrices.pickle"), "wb") as f:
            pickle.dump(self.od_matrices, f)
