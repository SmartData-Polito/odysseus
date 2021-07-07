#"bre-cambiato"
import datetime
import pickle
import warnings
warnings.simplefilter("ignore", UserWarning)
import os
import json
import argparse
import shutil
from odysseus.simulator.simulation_input.sim_input_paths import simulation_input_paths
from odysseus.simulator.single_run.single_run import single_run
from odysseus.simulator.multiple_runs.multiple_runs import multiple_runs
from odysseus.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid
from odysseus.simulator.simulation_input.sim_current_config.multiple_runs_conf import sim_scenario_conf_grid
from odysseus.simulator.simulation_input.sim_current_config.single_run_conf import sim_scenario_conf

def str2bool(string):
    if isinstance(string, bool):
        return string
    return True if string.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'] else False

parser = argparse.ArgumentParser()

parser.add_argument(
    "--n_cpus",
    help="specify max number of cpus to be used"
)
print(datetime.datetime.now())

#questa parte la rimpiazziamo con linea di comando
"""
with open(simulation_input_paths['sim_configs_target'], 'r') as my_file:
    data = my_file.read()
campaign_name = json.loads(data)['campaign_name']
conf_name = json.loads(data)['config_names'][0]
"""

parser.add_argument(
    "-c", "--campaign_name", nargs="+",
    help="specify campaign name"
)

parser.add_argument(
    "-cc", "--conf_name", nargs="+",
    help="specify conf name(s)"
)
parser.add_argument(
    "-g", "--set_general_parameters",
    nargs="?",
    const=True,
    help="Specify if you want to change general parameters "
)
parser.add_argument(
    "-s", "--existing_supply_model_folder",
    nargs="+",
    help="Specify the folder in which is stored a supply model"
)
parser.add_argument(
    "-d", "--existing_demand_model_folder",
    nargs="+",
    help="Specify the folder in which is stored a supply model" # demand magari?
)
parser.set_defaults(
    campaign_name=["test_03_2021"],
    conf_names=["streamlit_test_trace"],
    set_general_parameters = False,
    existing_supply_model_folder = "brendan_1",
    existing_demand_model_folder = "brendan_1" #"default_demand_model"
)

args = parser.parse_args()

campaign_name = args.campaign_name[0]
conf_name = args.conf_names[0]

print(campaign_name, conf_name)

versioned_conf_path = os.path.join(
    simulation_input_paths["sim_configs_versioned"],
    campaign_name,
    conf_name
)
shutil.rmtree(simulation_input_paths["sim_current_config"])
shutil.copytree(versioned_conf_path, simulation_input_paths["sim_current_config"])
conf_path = versioned_conf_path

#guided parameter configuration
if args.set_general_parameters:
    print("""
        Welcome to the automatic parameter setting. 
        Press enter to select the default values between squares or enter your choice
    """)
    input("Press enter to continue")
    print("\n---------------SIM GENERAL CONFIG---------------")
    city = [input("City? [Torino] \t\t\t") or "Torino"]
    data_source_id = [input("Data source id? [big_data_db] \t\t") or "big_data_db"]
    year = [int(input("Year? [2017] \t\t\t\t") or 2017)]
    month_start = [int(input("Starting month? [10] \t\t\t") or 10)]
    month_end = [int(input("Ending month? [11] \t\t\t") or 11)]
    sim_run_mode = [input("Sim run mode? [single_run] \t\t") or "single_run"]
    sim_technique = [input("Simulation technique? [eventG] \t\t") or "eventG"]
    sim_scenario_name = [input("Simulation scenario name? ["+str(args.conf_names[0])+"] ") or str(args.conf_names[0])]
   #probabilmente inutili
    const_load_factor = [str2bool(input("Const load factor? [False] \t\t") or False)]
    bin_side_length = [int(input("Bin side length [500] \t\t\t") or 500)]
    k_zones_factor = [int(input("K zones factor? [1] \t\t\t") or 1)]
    ###

    save_history = [str2bool(input("Save history? [False] \t\t\t") or False)]

    sim_general_conf_grid = {
        "city":city, "data_source_id":data_source_id, "year":year, "month_start":month_start, "month_end":month_end,
        "sim_run_mode":sim_run_mode, "sim_technique":sim_technique, "sim_scenario_name":sim_scenario_name,
        "const_load_factor":const_load_factor, "bin_side_length":bin_side_length, "k_zones_factor":k_zones_factor,
        "save_history":save_history
    }
    input("Parameters set successfully. Press enter to continue")
else:
    #read the default from the file
    from odysseus.simulator.simulation_input.sim_current_config.sim_general_conf import sim_general_conf_grid


#retrieving an existing SupplyModel template
if args.existing_supply_model_folder is not None:
    folder = args.existing_supply_model_folder
    folder_path = os.path.join(os.curdir, "odysseus", "supply_modelling", "supply_models", sim_general_conf_grid["city"][0], folder)#folder[0]) folder is a str not list :/

    if not os.path.exists(os.path.join(os.curdir, "odysseus", "supply_modelling", "supply_models",
                               sim_general_conf_grid["city"][0])):
        print("No "+args.cities[0]+" data stored.")
        exit(3)

    if not os.path.exists(folder_path):
        print(f"supply model path that i am trying to reach {folder_path}")
        print("Non-existent folder.")
        print("Available folders", str(os.listdir(os.path.join(os.curdir, "odysseus", "supply_modelling", "supply_models", sim_general_conf_grid["city"][0]))))
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
    #modello di offerta inesistente
    supply_model = None


#retrieving an existing DemandModel template

demand_folder = args.existing_demand_model_folder #[0] # this is not a list, it is a string :/
print(f"demand model folder args line 151 main simulator {demand_folder}, full list {args.existing_demand_model_folder}")
folder_path = os.path.join(os.curdir, "odysseus", "demand_modelling", "demand_models", sim_general_conf_grid["city"][0], demand_folder)

if not os.path.exists(os.path.join(os.curdir, "odysseus", "demand_modelling", "demand_models",
                               sim_general_conf_grid["city"][0])):
    print("No "+args.cities[0]+" data stored.")
    exit(2)

if not os.path.exists(folder_path):
    print("folder_path in simulator main",folder_path)
    print("Non-existent demand model folder.")
    print("Available folders", str(os.listdir(os.path.join(os.curdir, "odysseus", "demand_modelling", "demand_models", sim_general_conf_grid["city"][0]))))
    exit(1)


confs_dict = {}
confs_dict["multiple_runs"] = sim_scenario_conf_grid
confs_dict["single_run"] = sim_scenario_conf

sim_general_conf_list = EFFCS_SimConfGrid(sim_general_conf_grid).conf_list
for sim_general_conf in sim_general_conf_list:
    sim_run_mode = sim_general_conf["sim_run_mode"]
    print(sim_general_conf)

    parameters_dict = {
        "sim_general_conf":sim_general_conf,
        "sim_scenario_conf":confs_dict[sim_general_conf["sim_run_mode"]],
        "sim_scenario_name":sim_general_conf["sim_scenario_name"],
        "supply_model_object":supply_model,
        "demand_model_folder":demand_folder
    }

    if sim_run_mode == "single_run":
        single_run(
            parameters_dict
        )

    elif sim_run_mode == "multiple_runs":
        if args.n_cpus is not None:
            parameters_dict["n_cpus"] = int(args.n_cpus)
            multiple_runs(
                parameters_dict
            )
        else:
            multiple_runs(
                parameters_dict
            )
