import argparse
import datetime
import pickle
import warnings
warnings.simplefilter("ignore", UserWarning)

from odysseus.city_data_manager.config.config import *
from odysseus.simulator.simulation_input.sim_input_paths import simulation_input_paths
from odysseus.simulator.single_run.single_run import single_run
from odysseus.simulator.multiple_runs.multiple_runs import multiple_runs
from odysseus.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid
from odysseus.utils.path_utils import *

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
    "-s", "--existing_supply_model_folder",
    help="Specify the folder in which is stored a supply model"
)

parser.add_argument(
    "-d", "--existing_demand_model_folder",
    help="Specify the folder in which is stored a supply model"
)

parser.set_defaults(
    campaign_name="test",
    conf_name="big_data_db_test",
    existing_supply_model_folder=None,
    existing_demand_model_folder="isc2_extension_2021"
)

args = parser.parse_args()

campaign_name = args.campaign_name
conf_name = args.conf_name

versioned_conf_path = os.path.join(
    simulation_input_paths["sim_configs_versioned"],
    campaign_name,
    conf_name,
)

sim_general_conf_grid = get_sim_configs_from_path(versioned_conf_path, "sim_general_conf", "sim_general_conf_grid")
single_run_conf_grid = get_sim_configs_from_path(versioned_conf_path, "single_run_conf", "sim_scenario_conf")
multiple_runs_conf_grid = get_sim_configs_from_path(versioned_conf_path, "multiple_runs_conf", "sim_scenario_conf_grid")

print(sim_general_conf_grid)

confs_dict = dict()
confs_dict["multiple_runs"] = multiple_runs_conf_grid
confs_dict["single_run"] = single_run_conf_grid

sim_general_conf_list = EFFCS_SimConfGrid(sim_general_conf_grid).conf_list

for general_conf_id, sim_general_conf in enumerate(sim_general_conf_list):

    sim_general_conf["general_conf_id"] = general_conf_id

    sim_run_mode = sim_general_conf["sim_run_mode"]

    if args.existing_supply_model_folder is not None:
        existing_supply_model_folder = args.existing_supply_model_folder
        city_supply_models_path = os.path.join(supply_models_path, sim_general_conf["city"])
        folder_path = os.path.join(city_supply_models_path, existing_supply_model_folder)
        if not os.path.exists(city_supply_models_path):
            print("No supply model found for " + sim_general_conf["city"] + "!")
            exit(3)

        if not os.path.exists(folder_path):
            print("Non-existent folder.")
            print("Available folders", str(os.listdir(existing_supply_model_folder)))
            exit(1)
        else:
            if "supply_model.pickle" not in os.listdir(folder_path):
                print("The folder must contain the supply_model.pickle file")
                exit(2)
            else:
                print("Existing object. I am recovering it...")
                with open(os.path.join(folder_path, "supply_model.pickle"), "rb") as f:
                    supply_model = pickle.load(f)
    else:
        supply_model = None

    existing_demand_model_folder = args.existing_demand_model_folder
    city_demand_models_path = os.path.join(demand_models_path, sim_general_conf["city"])
    folder_path = os.path.join(city_demand_models_path, existing_demand_model_folder)

    if not os.path.exists(city_demand_models_path):
        print("No demand model found for " + sim_general_conf["city"] + "!")
        exit(2)

    if not os.path.exists(folder_path):
        print("Non-existent demand model folder.")
        print("Available folders", str(os.listdir(city_demand_models_path)))
        exit(1)

    parameters_dict = {
        "sim_general_conf": sim_general_conf,
        "sim_scenario_conf": confs_dict[sim_general_conf["sim_run_mode"]],
        "sim_scenario_name": sim_general_conf["sim_scenario_name"],
        "supply_model_object": supply_model,
        "demand_model_folder": existing_demand_model_folder
    }

    if sim_run_mode == "single_run":
        print(single_run_conf_grid)
        sim_conf_grid = EFFCS_SimConfGrid(single_run_conf_grid)
        pool_stats_dict = {}
        conf_tuples = []
        for conf_id, sim_scenario_conf in enumerate(sim_conf_grid.conf_list):
            parameters_dict["sim_scenario_conf"] = sim_scenario_conf
            parameters_dict["sim_scenario_conf"]["conf_id"] = "_".join([str(general_conf_id), str(conf_id)])
            single_run(
                parameters_dict
            )

    elif sim_run_mode == "multiple_runs":
        print(multiple_runs_conf_grid)
        parameters_dict["sim_general_conf"]["save_history"] = False
        if args.n_cpus is not None:
            parameters_dict["n_cpus"] = int(args.n_cpus)
            multiple_runs(
                parameters_dict
            )
        else:
            multiple_runs(
                parameters_dict
            )
