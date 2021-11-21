import os
import argparse
from odysseus.city_scenario.dummy_city_scenario.dummy_city_scenario import DummyCityScenario

from odysseus.simulator.simulation_input.sim_config_grid import SimConfGrid

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--city", nargs="+",
    help="specify dummy city"
)

parser.add_argument(
    "-b", "--bin_side_length", nargs="+",
    help="specify bin side length"
)

parser.add_argument(
    "-f", "--folder_name", nargs="+",
    help="Specify saving folder name "
)


parser.set_defaults(
    city="dummy_city",
    bin_side_length=500,
    folder_name="default"
)


args = parser.parse_args()
print(args)

dummy_city_scenario = DummyCityScenario(args.city, args.bin_side_length)
print(dummy_city_scenario.bookings_train)
print(dummy_city_scenario.bookings_test)
print(list(dummy_city_scenario.grid.geometry.apply(lambda g: str(g))))
print(dummy_city_scenario.grid_matrix)
