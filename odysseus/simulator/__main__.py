import argparse
import datetime
import pickle
import warnings

from odysseus.simulator.simulation_input.sim_input_paths import simulation_input_paths
from odysseus.simulator.simulation_run.single_run import single_run
from odysseus.simulator.simulation_run.multiple_runs import multiple_runs
from odysseus.simulator.simulation_input.sim_config_grid import SimConfGrid
from odysseus.utils.path_utils import *
from odysseus.path_config.path_config import *


warnings.simplefilter("ignore", UserWarning)

start = datetime.datetime.now()

parser = argparse.ArgumentParser()


parser.add_argument(
    "--n_cpus",
    help="specify max number of cpus to be used"
)
print(datetime.datetime.now())

parser.add_argument(
    "-c", "--campaign_name",
    help="specify campaign name"
)

parser.add_argument(
    "-cc", "--conf_name",
    help="specify conf name"
)

parser.add_argument(
    "-sf", "--city_scenario_folder",
    help="specify city scenario folder name"
)

parser.set_defaults(
    campaign_name="smartdata_test_0",
    conf_name="scenario_D",
    city_scenario_folder="escooters",
    sim_run_mode="single_run"
)

args = parser.parse_args()

campaign_name = args.campaign_name
conf_name = args.conf_name

versioned_conf_path = os.path.join(
    simulation_input_paths["sim_configs_versioned"],
    campaign_name,
    conf_name,
)
print(versioned_conf_path)

sim_general_conf_grid = get_sim_configs_from_path(versioned_conf_path, "sim_general_conf", "sim_general_config_grid")
demand_model_conf_grid = get_sim_configs_from_path(versioned_conf_path, "demand_model_conf", "demand_model_config_grid")
supply_model_conf_grid = get_sim_configs_from_path(versioned_conf_path, "supply_model_conf", "supply_model_config_grid")

config_grids_dict = dict()
config_grids_dict["sim_general_config_grid"] = sim_general_conf_grid
config_grids_dict["demand_model_config_grid"] = demand_model_conf_grid
config_grids_dict["supply_model_config_grid"] = supply_model_conf_grid

try:
    sim_general_conf_list = SimConfGrid(sim_general_conf_grid).conf_list
    configs_list = list()
    conf_id = 0
    for general_conf_id, sim_general_conf in enumerate(sim_general_conf_list):
        sim_general_conf["general_conf_id"] = general_conf_id
        demand_conf_grid = SimConfGrid(demand_model_conf_grid)
        for demand_conf_id, demand_model_conf in enumerate(demand_conf_grid.conf_list):
            supply_conf_grid = SimConfGrid(supply_model_conf_grid)
            for supply_model_conf_id, supply_model_conf in enumerate(supply_conf_grid.conf_list):
                parameters_dict = {
                    "city_scenario_folder": args.city_scenario_folder,
                    "sim_general_conf": sim_general_conf,
                    "sim_scenario_name": sim_general_conf["sim_scenario_name"],
                    "demand_model_conf": demand_model_conf,
                    "supply_model_conf": supply_model_conf,
                    "supply_model_object": None,
                    "conf_id": "_".join(
                        [str(general_conf_id), str(demand_conf_id), str(supply_model_conf_id)]
                    )
                }
                configs_list.append(parameters_dict)
                conf_id += 1

except Exception:
    print("Simulator not properly configured!")
    exit()

if args.sim_run_mode == "single_run":
    for parameters_dict in configs_list:
        single_run(parameters_dict)
        exit()

elif args.sim_run_mode == "multiple_runs":
    for parameters_dict in configs_list:
        parameters_dict["sim_general_conf"]["history_to_file"] = False
        for k in parameters_dict["sim_general_conf"]:
            if "exclude" in k:
                parameters_dict["sim_general_conf"][k] = True
        if args.n_cpus is not None:
            parameters_dict["n_cpus"] = int(args.n_cpus)
    multiple_runs(config_grids_dict, configs_list)

else:
    print("Unknown run mode: {}".format(args.sim_run_mode))

end = datetime.datetime.now()

print("Total execution time:", (end-start).total_seconds())
