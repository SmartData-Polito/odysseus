import os
import argparse
import datetime

from odysseus.demand_modelling.demand_model import DemandModel
from odysseus.demand_modelling.demand_models.hourly_ods_count import HourlyODsCountDemandModel

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
    "-t", "--demand_model_type", nargs="+",
    help="specify demand model type"
)
parser.add_argument(
    "-k", "--kde_bandwidth", nargs="+",
    help="specify kde bandwidths"
)

parser.add_argument(
    "-C", "--city_scenario_folder", nargs="+",
    help="Specify city scenario folder name "
)

parser.add_argument(
    "-D", "--city_demand_model_folder", nargs="+",
    help="Specify city demand model folder name "
)

parser.set_defaults(

    city=["Louisville"],
    data_source_id=["city_open_data"],
    demand_model_type=["hourly_ods_count"],
    kde_bandwidth=["1"],
    city_scenario_folder=["default"],
    city_demand_model_folder=["hourly_ods_count_trial"],

)

args = parser.parse_args()
demand_model_configs_grid = vars(args)

demand_model_configs_list = SimConfGrid(demand_model_configs_grid).conf_list

for demand_model_config in demand_model_configs_list:

    print(args.demand_model_type)

    if demand_model_config["demand_model_type"] == "hourly_ods_count":
        demand_model = HourlyODsCountDemandModel(
            demand_model_config["city"],
            demand_model_config["data_source_id"],
            demand_model_config
        )
    else:
        demand_model = DemandModel(
            demand_model_config["city"],
            demand_model_config["data_source_id"],
            demand_model_config
        )

    demand_model.fit_model()
    booking_requests_list = demand_model.generate_booking_requests_list(
        datetime.datetime(2022, 1, 1),
        datetime.datetime(2022, 1, 2),
    )
    demand_model.save_results()
