import os
from odysseus.demand_modelling.demand_model import DemandModel
from odysseus.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid
from odysseus.demand_modelling.demand_model_configs.default_config import demand_model_configs_grid
from odysseus.webapp.apis.api_cityDataManager.utils import *

DEFAULT_FORM = {
    "cities":["Torino", "Milano", "Vancouver"],
    "data_source_ids":["big_data_db"],
    "sim_techniques":["eventG"],
    "bin_side_lengths":["500"],
    "zones_factors":["1"],
    "kde_bandwidths":["1"],
    "train_range":["2017", "10", "2017", "10"],
    "test_range":["2017", "11", "2017", "11"]
}

class DemandModelling:
    def __init__(self, form_inputs=DEFAULT_FORM):

        self.cities = form_inputs["cities"]
        self.data_source_ids = form_inputs["data_source_ids"]
        self.sim_techniques = form_inputs["sim_techniques"]
        self.bin_side_lengths = form_inputs["bin_side_lengths"]
        self.zones_factors = form_inputs["zones_factors"]
        self.kde_bandwidths=form_inputs["kde_bandwidths"]
        self.train_range = form_inputs["train_range"]
        self.test_range = form_inputs["test_range"]
        
        self.demand_model_configs_grid = {
            "city": self.cities,

            "data_source_id": self.data_source_ids,
            "sim_technique": self.sim_techniques,

            "bin_side_length": list(map(int, self.bin_side_lengths)),
            "k_zones_factor": list(map(int, self.zones_factors)),
            "kde_bandwidth": list(map(int, self.kde_bandwidths)),
        }
    def run(self):
        
        demand_model_configs_list = EFFCS_SimConfGrid(self.demand_model_configs_grid).conf_list
        print("demand_model_configs_list", demand_model_configs_list)
        for demand_model_config in demand_model_configs_list:

            print("demand_model_config",demand_model_config)

            # demand_model_path = os.path.join(
            #     os.path.dirname(os.path.dirname(__file__)),
            #     "demand_modelling",
            #     "demand_models",
            #     demand_model_config["city"],
            # )
            ROOT_DIR = os.path.abspath(os.curdir)
            
            demand_model_path = os.path.join(
                ROOT_DIR,
                "odysseus",
                "demand_modelling",
                "demand_models",
                demand_model_config["city"],
            )
            os.makedirs(demand_model_path, exist_ok=True)

            if not os.path.exists(os.path.join(demand_model_path, "city_obj.pickle")):
                demand_model = DemandModel(demand_model_config["city"], demand_model_config,
                                        int(self.train_range[0]), int(self.train_range[1]),
                                        int(self.train_range[2]), int(self.train_range[3]),
                                        int(self.test_range[0]), int(self.test_range[1]),
                                        int(self.test_range[2]), int(self.test_range[3]))
                demand_model.save_results()
                if self.in_flow:
                    demand_model.save_in_flow_count()
                if self.out_flow:
                    demand_model.save_out_flow_count()
                return {"status":"complete"}
            else:
                return {"status":"not_run"}
""" 
        for demand_model_config in demand_model_configs_list:

            print(demand_model_config)

            demand_model_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "demand_modelling",
                "demand_models",
                demand_model_config["city"],
            )
            os.makedirs(demand_model_path, exist_ok=True)

            if not os.path.exists(os.path.join(demand_model_path, "city_obj.pickle")):
                demand_model = DemandModel(demand_model_config["city"], demand_model_config)
                demand_model.save_results()
 """