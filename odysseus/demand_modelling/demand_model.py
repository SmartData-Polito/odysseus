import os
import json
import pickle

from odysseus.city_scenario.city_scenario_from_wgs84_trips import CityScenarioFromTrips

from odysseus.utils.bookings_utils import *


class DemandModel:

    def __init__(
            self,
            city_name,
            data_source_id,
            demand_model_config,
            grid_crs
    ):

        self.demand_model_config = demand_model_config

        self.city_name = city_name
        self.data_source_id = data_source_id

        self.city_scenario_folder = self.demand_model_config["city_scenario_folder"]
        self.city_scenario_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "city_scenario",
            "city_scenarios",
            self.city_name,
            self.city_scenario_folder
        )
        self.demand_model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "demand_modelling",
            "city_demand_models",
            self.city_name,
            self.city_scenario_folder
        )
        os.makedirs(self.demand_model_path, exist_ok=True)

        self.city_scenario = CityScenarioFromTrips(
            city_name=self.city_name,
            data_source_id=self.data_source_id,
            read_config_from_file=True,
            in_folder_name=self.city_scenario_folder
        )
        self.city_scenario.read_city_scenario_for_demand_model()

        self.bookings_train = self.city_scenario.bookings_train
        self.grid = self.city_scenario.grid
        self.grid_matrix = self.city_scenario.grid_matrix
        self.closest_valid_zone = self.city_scenario.closest_valid_zone
        self.bin_side_length = self.city_scenario.bin_side_length
        self.grid_crs = grid_crs
        self.numerical_params_dict = self.city_scenario.numerical_params_dict
        self.avg_speed_kmh_mean = self.numerical_params_dict["avg_speed_mean"]
        self.avg_speed_kmh_std = self.numerical_params_dict["avg_speed_std"]
        self.max_driving_distance = self.numerical_params_dict["max_driving_distance"]

        self.distance_matrix = self.city_scenario.distance_matrix

        self.max_out_flow = float('-inf')
        self.max_in_flow = float('-inf')

        self.booking_requests_list = list()
        self.od_matrices = dict()
        self.week_config = dict()

    def fit_model(self):
        pass

    def generate_booking_requests_list(
            self,
            start_datetime,
            end_datetime,
            requests_rate_factor
    ):
        pass

    def generate_booking_requests_sim(
            self,
            start_datetime,
            requests_rate_factor,
            avg_speed_kmh_mean,
            max_duration,
            fixed_driving_distance
    ):
        pass

    def save_config(self):

        os.makedirs(self.demand_model_path, exist_ok=True)

        with open(os.path.join(self.demand_model_path, "demand_model_config.json"), "w") as f:
            json.dump(self.demand_model_config, f, sort_keys=True, indent=4)

        with open(os.path.join(self.demand_model_path, "week_config.json"), "w") as f:
            json.dump(self.week_config, f, sort_keys=True, indent=4)

    def save_results(self):
        pass

