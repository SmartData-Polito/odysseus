import os
import argparse

from odysseus.demand_modelling.demand_model import DemandModel

from odysseus.simulator.simulation_input.sim_config_grid import SimConfGrid

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--city", nargs="+",
    help="specify cities"
)

parser.add_argument(
    "-d", "--data_source_id", nargs="+",
    help="specify data source ids"
)

parser.add_argument(
    "-k", "--kde_bandwidth", nargs="+",
    help="specify kde bandwidths"
)

parser.add_argument(
    "-C", "--city_scenario_folder", nargs="+",
    help="Specify city scenario folder name "
)

parser.set_defaults(
    city=["Louisville"],
    data_source_id=["city_open_data"],
    kde_bandwidth=["1"],
    city_scenario_folder=["default"],
)

args = parser.parse_args()
demand_model_configs_grid = vars(args)

demand_model_configs_list = SimConfGrid(demand_model_configs_grid).conf_list

for demand_model_config in demand_model_configs_list:

    print(demand_model_config)
    demand_model = DemandModel(demand_model_config)
    demand_model.save_results()
