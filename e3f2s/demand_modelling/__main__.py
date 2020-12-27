import os
import argparse

from e3f2s.demand_modelling.demand_model import DemandModel

from e3f2s.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid

from e3f2s.simulator.simulation_input.sim_current_config.sim_general_conf import sim_general_conf_grid
from e3f2s.simulator.simulation_input.sim_current_config.multiple_runs_conf import sim_scenario_conf_grid
from e3f2s.simulator.simulation_input.sim_current_config.single_run_conf import sim_scenario_conf

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

sim_general_conf_list = EFFCS_SimConfGrid(sim_general_conf_grid).conf_list
for sim_general_conf in sim_general_conf_list:
    sim_run_mode = sim_general_conf["sim_run_mode"]
    print(sim_general_conf)

    demand_model_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "demand_modelling",
        "demand_models",
        sim_general_conf["city"],
    )
    os.makedirs(demand_model_path, exist_ok=True)

    if not os.path.exists(os.path.join(demand_model_path, "city_obj.pickle")):
        city_obj = DemandModel(sim_general_conf["city"], sim_general_conf)
        city_obj.save_results()
