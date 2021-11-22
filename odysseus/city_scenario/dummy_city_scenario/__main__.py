import argparse
from odysseus.city_scenario.dummy_city_scenario.dummy_city_scenario import DummyCityScenario

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--city", nargs="+",
    help="specify dummy city"
)

parser.add_argument(
    "-d", "--data_source_id", nargs="+",
    help="specify data source ids"
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
    data_source_id="city_open_data",
    bin_side_length=500,
    folder_name="default"
)


args = parser.parse_args()
print(args)

dummy_city_scenario = DummyCityScenario(args.city, args.data_source_id, args.bin_side_length)
print(dummy_city_scenario.bookings_train)
print(dummy_city_scenario.bookings_test)
print(list(dummy_city_scenario.grid.geometry.apply(lambda g: str(g))))
print(dummy_city_scenario.grid_matrix)

dummy_city_scenario.create_city_scenario_from_trips_data()
dummy_city_scenario.save_results()
