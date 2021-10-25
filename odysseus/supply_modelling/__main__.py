import argparse
from odysseus.supply_modelling.supply_model import SupplyModel

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
    "-v", "--n_vehicles", nargs="+",
    help="specify num vehicles"
)

parser.add_argument(
    "-p", "--tot_n_charging_poles", nargs="+",
    help="specify total number of charging poles"
)

parser.add_argument(
    "-z", "--n_charging_zones", nargs="+",
    help="specify number of charging zones"
)

parser.add_argument(
    "-y", "--year", nargs="+",
    help="specify year"
)

parser.add_argument(
    "-a", "--distributed_cps", nargs="+",
    help="specify if cps are distributed (True or False)"
)

available_policy = ["num_parkings", "old_manual", "real_positions", "realpos_numpark"]

parser.add_argument(
    "-pp", "--cps_placement_policy", nargs="+",
    help="specify placement policy. Available options: "+str(available_policy)
)

parser.add_argument(
    "-w", "--n_relocation_workers", nargs="+",
    help="Specify number of relocation workers"
)
parser.add_argument(
    "-f", "--folder_name", nargs="+",
    help="Specify saving folder name "
)

default = {
    "city": ["Louisville"],
    "data_source_id": ["city_open_data"],
    "n_vehicles": ["500"],
    "tot_n_charging_poles": ["100"],
    "n_charging_zones": ["10"],
    "year": ["2017"],
    "distributed_cps": ["True"],
    "cps_placement_policy": ["num_parkings"],
    "n_relocation_workers": [1],
    "city_scenario_folder": ["default"],
    "folder_name": ["default"],
}


parser.set_defaults(

    city=default["city"],
    data_source_id=default["data_source_id"],

    n_vehicles=default["n_vehicles"],
    tot_n_charging_poles=default["tot_n_charging_poles"],
    n_charging_zones=default["n_charging_zones"],
    year=default["year"],
    distributed_cps=default["distributed_cps"],
    cps_placement_policy=default["cps_placement_policy"],
    n_relocation_workers=default["n_relocation_workers"],

    city_scenario_folder=default["city_scenario_folder"],
    folder_name=default["folder_name"],

)


args = parser.parse_args()

supply_model_configs_grid = vars(args)

supply_model_configs_list = SimConfGrid(supply_model_configs_grid).conf_list

for supply_model_config in supply_model_configs_list:

    print(supply_model_config)

    supply_model = SupplyModel(supply_model_config)
    vehicles_soc_dict, vehicles_zones, available_vehicles_dict = supply_model.init_vehicles()
    supply_model.init_charging_poles()
    supply_model.init_relocation()
