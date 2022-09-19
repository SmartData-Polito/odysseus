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

        self.city_scenario = CityScenarioFromTrips(
            city_name=self.city_name,
            data_source_id=self.data_source_id,
            read_config_from_file=True,
            in_folder_name=self.city_scenario_folder
        )
        self.city_scenario.read_city_scenario_for_demand_model()
        self.bookings_train = self.city_scenario.bookings_train
        self.grid = self.city_scenario.grid

        self.max_out_flow = float('-inf')
        self.max_in_flow = float('-inf')

        self.booking_requests_list = list()

    def fit_model(self):
        pass

    def generate_booking_requests_list(self, start_datetime, end_datetime):
        pass

    def generate_booking_requests_sim(self):
        pass

    def save_config(self):

        os.makedirs(self.demand_model_path, exist_ok=True)

        with open(os.path.join(self.demand_model_path, "demand_model_config.json"), "w") as f:
            json.dump(self.demand_model_config, f, sort_keys=True, indent=4)

    def save_results(self):
        pass

