import os
import argparse

from odysseus.city_scenario.city_scenario import CityScenario

from odysseus.simulator.simulation_input.sim_config_grid import SimConfGrid

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--cities", nargs="+",
    help="specify cities"
)

parser.add_argument(
    "-d", "--data_source_ids", nargs="+",
    help="specify data source ids"
)

parser.add_argument(
    "-b", "--bin_side_lengths", nargs="+",
    help="specify bin side lengths"
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
    cities=["Louisville"],
    data_source_ids=["city_open_data"],
    sim_techniques=["eventG"],
    bin_side_lengths=["500"],
    kde_bandwidths=["1"],
    train_range=["2019", "1", "2019", "1"],
    test_range=["2019", "2", "2019", "2"],
    folder_name=["default"]
)

args = parser.parse_args()

city_scenario_configs_grid = {
    "city": args.cities,
    "data_source_id": args.data_source_ids,
    "bin_side_length": list(map(int, args.bin_side_lengths)),
}

city_scenario_configs_list = SimConfGrid(city_scenario_configs_grid).conf_list

for city_scenario_config in city_scenario_configs_list:

    print(city_scenario_config)

    city_scenario = CityScenario(city_scenario_config["city"], city_scenario_config, save_folder=args.folder_name[0])
    city_scenario.create_city_scenario(
        int(args.train_range[0]), int(args.train_range[1]),
        int(args.train_range[2]), int(args.train_range[3]),
        int(args.test_range[0]), int(args.test_range[1]),
        int(args.test_range[2]), int(args.test_range[3]),
    )
    city_scenario.save_results()
