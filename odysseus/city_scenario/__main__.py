import os
import argparse

from odysseus.city_scenario.city_scenario_from_wgs84_trips import CityScenarioFromTrips
from odysseus.city_scenario.city_scenario_from_virtual_od import CityScenarioFromOD
from odysseus.simulator.simulation_input.sim_config_grid import SimConfGrid

parser = argparse.ArgumentParser()

parser.add_argument(
    "-D", "--data_from", nargs="+",
    help="specify where to get data from"
)

parser.add_argument(
    "-c", "--city", nargs="+",
    help="specify cities"
)

parser.add_argument(
    "-d", "--data_source_id", nargs="+",
    help="specify data source ids"
)

parser.add_argument(
    "-b", "--bin_side_length", nargs="+",
    help="specify bin side lengths",
    type=int
)

parser.add_argument(
    "-T", "--train_range", nargs=4,
    help="specify start year, start month, end year and end month for training"
)

parser.add_argument(
    "-t", "--test_range", nargs=4,
    help="specify start year, start month, end year and end month for testing"
)

parser.add_argument(
    "-f", "--folder_name", nargs="+",
    help="Specify saving folder name "
)


parser.set_defaults(
    data_from=["od"],
    city=["my_city_3X3_generated"],
    data_source_id=["my_data_source"],
    bin_side_length=[500],
    train_range=("2017", "1", "2017", "1"),
    test_range=("2017", "1", "2017", "1"),
    folder_name=["default"]
)

args = parser.parse_args()
city_scenario_configs_grid = vars(args)
city_scenario_configs_grid["train_range"] = [tuple(city_scenario_configs_grid["train_range"])]
city_scenario_configs_grid["test_range"] = [tuple(city_scenario_configs_grid["test_range"])]
city_scenario_configs_list = SimConfGrid(city_scenario_configs_grid).conf_list

for city_scenario_config in city_scenario_configs_list:

    if city_scenario_config["data_from"] == "trips":

        print(city_scenario_config)
        city_scenario = CityScenarioFromTrips(
            city_name=city_scenario_config["city"],
            data_source_id=city_scenario_config["data_source_id"],
            city_scenario_config=city_scenario_config,
            read_config_from_file=False,
        )

        city_scenario.init_train_test(
            int(city_scenario_config["train_range"][0]), int(city_scenario_config["train_range"][1]),
            int(city_scenario_config["train_range"][2]), int(city_scenario_config["train_range"][3]),
            int(city_scenario_config["test_range"][0]), int(city_scenario_config["test_range"][1]),
            int(city_scenario_config["test_range"][2]), int(city_scenario_config["test_range"][3]),
        )
        city_scenario.create_squared_city_grid()

    elif city_scenario_config["data_from"] == "od":

        print(city_scenario_config)
        city_scenario = CityScenarioFromOD(
            city_scenario_config["city"], "my_data_source", city_scenario_config=city_scenario_config
        )

    else:

        city_scenario = None

    if city_scenario:
        city_scenario.create_city_scenario_from_trips_data()
        city_scenario.save_results()
    else:
        print("City Scenario not configured properly!")
