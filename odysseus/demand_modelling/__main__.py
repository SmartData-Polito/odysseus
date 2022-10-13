import os
import argparse
import datetime

from odysseus.demand_modelling.demand_model import DemandModel
from odysseus.demand_modelling.demand_models.poisson_kde import PoissonKdeDemandModel
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

    city=["my_city_3X3_generated"],
    data_source_id=["my_data_source"],
    demand_model_type=["poisson_kde"],
    kde_bandwidth=["1"],
    city_scenario_folder=["default"],
    city_demand_model_folder=["default"],

)

args = parser.parse_args()
demand_model_configs_grid = vars(args)

demand_model_configs_list = SimConfGrid(demand_model_configs_grid).conf_list

for demand_model_config in demand_model_configs_list:

    demand_model = None

    if demand_model_config["demand_model_type"] == "hourly_ods_count":
        demand_model = HourlyODsCountDemandModel(
            demand_model_config["city"],
            demand_model_config["data_source_id"],
            demand_model_config
        )
    elif demand_model_config["demand_model_type"] == "poisson_kde":
        demand_model = PoissonKdeDemandModel(
            demand_model_config["city"],
            demand_model_config["data_source_id"],
            demand_model_config
        )

    demand_model.fit_model()
    # booking_requests_list = demand_model.generate_booking_requests_list(
    #     datetime.datetime(2022, 1, 1),
    #     datetime.datetime(2022, 1, 2),
    # )
    demand_model.save_results()
