import os
import argparse

from odysseus.demand_modelling.demand_model import DemandModel

from odysseus.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid

from odysseus.demand_modelling.demand_model_configs.default_config import demand_model_configs_grid

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--cities", nargs="+",
    help="specify cities"
)

parser.add_argument(
    "-y", "--years", nargs="+",
    help="specify years"
)

parser.add_argument(
    "-m", "--months", nargs="+",
    help="specify months"
)

parser.add_argument(
    "-d", "--data_source_ids", nargs="+",
    help="specify data source ids"
)


parser.set_defaults(
    cities=["Torino", "Milano", "Vancouver"],
    data_source_ids=["big_data_db"],
    years=["2017"],
    months=["10", "11", "12"],
)

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
