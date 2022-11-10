import os
import argparse
import pickle

from odysseus.demand_modelling.trips_demand_models.poisson_kde import PoissonKdeDemandModel
from odysseus.demand_modelling.trips_demand_models.hourly_ods_count import HourlyODsCountDemandModel
from odysseus.demand_modelling.od_demand_models.od_demand_model import ODmatricesDemandModel

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

    city=["my_city_1_1X5"],
    data_source_id=["my_data_source"],
    demand_model_type=["od_matrices"],
    kde_bandwidth=["0"],
    city_scenario_folder=["charging_zone"],
    city_demand_model_folder=["charging_zone"],

)

args = parser.parse_args()
demand_model_configs_grid = vars(args)

demand_model_configs_list = SimConfGrid(demand_model_configs_grid).conf_list

for demand_model_config in demand_model_configs_list:

    if demand_model_config["city"].startswith("my_city"):
        grid_crs = "epsg:3857"
    else:
        grid_crs = "epsg:4326"

    demand_model = None

    if demand_model_config["demand_model_type"] == "hourly_ods_count":
        demand_model = HourlyODsCountDemandModel(
            demand_model_config["city"],
            demand_model_config["data_source_id"],
            demand_model_config,
            grid_crs
        )
    elif demand_model_config["demand_model_type"] == "poisson_kde":
        demand_model = PoissonKdeDemandModel(
            demand_model_config["city"],
            demand_model_config["data_source_id"],
            demand_model_config,
            grid_crs
        )
    elif demand_model_config["demand_model_type"] == "od_matrices":
        demand_model = ODmatricesDemandModel(
            demand_model_config["city"],
            demand_model_config["data_source_id"],
            demand_model_config,
            grid_crs
        )

    demand_model.fit_model()
    demand_model.save_results()
    pickle.dump(
        demand_model,
        open(os.path.join(demand_model.demand_model_path, "demand_model.pickle"), "wb")
    )
