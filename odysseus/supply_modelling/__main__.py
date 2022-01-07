import argparse
from odysseus.supply_modelling.supply_model import SupplyModel

from odysseus.simulator.simulation_input.sim_config_grid import SimConfGrid

parser = argparse.ArgumentParser()

# ---> City and data source

parser.add_argument(
    "-c", "--city", nargs="+",
    help="specify cities"
)

parser.add_argument(
    "-d", "--data_source_id", nargs="+",
    help="specify data source ids"
)

# ---> Fleet

parser.add_argument(
    "-v", "--n_vehicles", nargs="+",
    help="specify num vehicles"
)

parser.add_argument(
    "-e", "--engine_type", nargs="+",
    help="specify engine type for vehicles in the fleet"
)

parser.add_argument(
    "-vm", "--vehicle_model_name", nargs="+",
    help="specify vehicle model among the supported ones"
)

# ---> Charging

parser.add_argument(
    "-p", "--tot_n_charging_poles", nargs="+",
    help="specify total number of charging poles"
)

parser.add_argument(
    "-z", "--n_charging_zones", nargs="+",
    help="specify number of charging zones"
)

parser.add_argument(
    "-a", "--distributed_cps", nargs="+",
    help="specify if cps are distributed (True or False)"
)

available_policy = ["num_parkings", "old_manual", "real_positions", "realpos_numpark"]

parser.add_argument(
    "-pp", "--cps_placement_policy", nargs="+",
    help="specify placement policy. Available options: " + str(available_policy)
)

parser.add_argument(
    "-w", "--n_relocation_workers", nargs="+",
    help="Specify number of relocation workers"
)

parser.add_argument(
    "-cf", "--city_scenario_folder", nargs="+",
    help="Specify city scenario folder name "
)

parser.add_argument(
    "-sf", "--supply_model_folder", nargs="+",
    help="Specify supply model folder name "
)

parser.set_defaults(

    city=["Louisville"],
    data_source_id=["city_open_data"],

    n_vehicles=["500"],
    engine_type=["electric"],
    vehicle_model_name=["generic e-scooter"],

    distributed_cps=[True],
    profile_type=["wall_plug"],
    cps_placement_policy=["num_parkings"],
    tot_n_charging_poles=["100"],
    n_charging_zones=["10"],

    n_relocation_workers=[1],

    city_scenario_folder=["default"],
    supply_model_folder=["test"],

)


args = parser.parse_args()

supply_model_configs_grid = vars(args)

supply_model_configs_list = SimConfGrid(supply_model_configs_grid).conf_list

for supply_model_config in supply_model_configs_list:

    supply_model = SupplyModel(
        supply_model_config["city"],
        supply_model_config["data_source_id"],
        supply_model_config["city_scenario_folder"],
        supply_model_config["supply_model_folder"],
        supply_model_config,
        init_from_map_json_config=True
    )
    supply_model.init_vehicles()
    supply_model.init_charging_poles()
    supply_model.init_relocation()
    supply_model.save_results()
