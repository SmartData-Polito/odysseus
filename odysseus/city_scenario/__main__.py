import datetime
import argparse
import warnings
warnings.filterwarnings("ignore")

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
    data_from=["trips"],
    city=["test_city"],
    data_source_id=["custom_trips"],
    bin_side_length=[500],
    train_range=("2020", "9", "2020", "9"),
    test_range=("2020", "9", "2020", "9"),
    folder_name=["test_scenario"]
)

args = parser.parse_args()
city_scenario_configs_grid = vars(args)
city_scenario_configs_grid["train_range"] = [tuple(city_scenario_configs_grid["train_range"])]
city_scenario_configs_grid["test_range"] = [tuple(city_scenario_configs_grid["test_range"])]
city_scenario_configs_list = SimConfGrid(city_scenario_configs_grid).conf_list

start = datetime.datetime.now()

for city_scenario_config in city_scenario_configs_list:

    if city_scenario_config["data_from"] == "trips":

        print(city_scenario_config)

        city_scenario = CityScenarioFromTrips(
            city_name=city_scenario_config["city"],
            data_source_id=city_scenario_config["data_source_id"],
            city_scenario_config=city_scenario_config,
            read_config_from_file=False,
        )

        print("Initialising train and test set..")
        city_scenario.init_train_test(
            int(city_scenario_config["train_range"][0]), int(city_scenario_config["train_range"][1]),
            int(city_scenario_config["train_range"][2]), int(city_scenario_config["train_range"][3]),
            int(city_scenario_config["test_range"][0]), int(city_scenario_config["test_range"][1]),
            int(city_scenario_config["test_range"][2]), int(city_scenario_config["test_range"][3]),
        )

        print("Initialising grid..")
        city_scenario.create_squared_city_grid()

        print("Creating city scenario..")
        city_scenario.create_city_scenario_from_trips_data()

    elif city_scenario_config["data_from"] == "od":

        print(city_scenario_config)
        city_scenario = CityScenarioFromOD(
            city_scenario_config["city"], city_scenario_config["data_source_id"],
            city_scenario_config=city_scenario_config
        )
        city_scenario.create_city_scenario_from_trips_data()
        city_scenario.save_virtual_od_results()

    else:

        city_scenario = None

    if city_scenario is not None:
        city_scenario.save_results()
    else:
        print("City Scenario not configured properly!")

end = datetime.datetime.now()

print("City scenario execution time:", (end-start).total_seconds())
