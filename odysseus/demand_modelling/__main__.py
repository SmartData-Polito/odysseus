import os
import argparse

from odysseus.demand_modelling.demand_model import DemandModel

from odysseus.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid

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
    "-s", "--sim_techniques", nargs="+",
    help="specify sim techniques"
)

parser.add_argument(
    "-b", "--bin_side_lengths", nargs="+",
    help="specify bin side lengths"
)

parser.add_argument(
    "-z", "--zones_factors", nargs="+",
    help="specify k zone factors"
)

parser.add_argument(
    "-k", "--kde_bandwidths", nargs="+",
    help="specify kde bandwidths"
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
    "--in_flow", action="store_true",
    help="compute in flows"
)

parser.add_argument(
    "--out_flow", action="store_true",
    help="compute out flows"
)


parser.set_defaults(
    cities=["Amsterdam"],
    data_source_ids=["big_data_db"],
    sim_techniques=["eventG"],
    bin_side_lengths=["500"],
    zones_factors=["1"],
    kde_bandwidths=["1"],
    train_range=["2017", "1", "2017", "1"],
    test_range=["2017", "2", "2017", "2"],
)

args = parser.parse_args()

demand_model_configs_grid = {
    "city": args.cities,

    "data_source_id": args.data_source_ids,
    "sim_technique": args.sim_techniques,

    "bin_side_length": list(map(int, args.bin_side_lengths)),
    "k_zones_factor": list(map(int, args.zones_factors)),
    "kde_bandwidth": list(map(int, args.kde_bandwidths)),
}

demand_model_configs_list = EFFCS_SimConfGrid(demand_model_configs_grid).conf_list

for demand_model_config in demand_model_configs_list:

    print(demand_model_config)

    demand_model_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "demand_modelling",
        "demand_models",
        demand_model_config["city"],
    )
    os.makedirs(demand_model_path, exist_ok=True)

    if not os.path.exists(os.path.join(demand_model_path, "city_obj.pickle")):
        demand_model = DemandModel(demand_model_config["city"], demand_model_config,
                                   int(args.train_range[0]), int(args.train_range[1]),
                                   int(args.train_range[2]), int(args.train_range[3]),
                                   int(args.test_range[0]), int(args.test_range[1]),
                                   int(args.test_range[2]), int(args.test_range[3]))
        demand_model.save_results()
        if args.in_flow:
            demand_model.save_in_flow_count()
        if args.out_flow:
            demand_model.save_out_flow_count()
