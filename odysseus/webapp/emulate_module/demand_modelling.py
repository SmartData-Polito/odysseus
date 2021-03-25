import os
from e3f2s.demand_modelling.demand_model import DemandModel
from e3f2s.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid
from e3f2s.demand_modelling.demand_model_configs.default_config import demand_model_configs_grid


class DemandModelling:
    def __init__(self, cities=["Torino"], years=[2017], months=["10", "11"], data_source_ids=["big_data_db"]):
        self.cities = cities
        self.years = years
        self.months = months
        self.data_source_ids = data_source_ids

    def run(self):

        demand_model_configs_list = EFFCS_SimConfGrid(demand_model_configs_grid).conf_list

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
