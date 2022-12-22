import argparse
import datetime

from odysseus.city_data_manager.od_matrices.virtual_od.od_generator import generate_trips_from_od
from odysseus.city_data_manager.od_matrices.virtual_od.virtual_od_data_source import *

parser = argparse.ArgumentParser()

parser.add_argument(
    "-c", "--city",
    help="specify city name"
)

parser.add_argument(
    "-d", "--data_source_id",
    help="specify data source id"
)

parser.add_argument(
    "-r", "--read", action="store_true",
    help="""
    If active, try to read a previously generated OD matrix and ignore other parameters
    If not active, generate a new OD matrix with specified parameters.
    """
)

parser.add_argument(
    "-ws", "--week_slots_type",
    help="specify how to divide days within a week", choices=["generic_day", "weekday_weekend"]
)

parser.add_argument(
    "-ds", "--day_slots_type",
    help="specify how to divide hours within a day", choices=["generic_hour", "daymoments", "hours"]
)

parser.add_argument(
    "-nh", "--n_hours",
    nargs=2, metavar=('train_hours', 'test_hours'),
    help="specify number of train hours and test hours to generate"
)

parser.add_argument(
    "-g", "--grid_params",
    nargs=3, metavar=('n_rows', 'n_cols', 'bin_side_length'),
    help="specify parameters to create the grid: number of rows, number of columns, size of squared cell",
)

parser.add_argument(
    "-od", "--od_params",
    nargs=2, metavar=('od_type', 'count', ),
    help="""
        specify od type and params to generate OD matrices.
        "uniform" requires parameter "count"
        "simple_cyclic" requires parameter "count"
    """,
)

parser.set_defaults(
    read=True,
    city="my_city",
    data_source_id="my_data_source",
    week_slots_type="generic_day",
    day_slots_type="generic_hour",
    n_hours=(24 * 1, 24 * 1),
    grid_params=(1, 5, 500),
    od_params=("uniform_single_destination", 1, ()),
)

args = parser.parse_args()

od_data_source = VirtualODDataSource(args.city, args.data_source_id)

start = datetime.datetime.now()

if not args.read:

    print("Generating OD..")
    od_matrices_by_dayslots, od_matrices_by_hour, grid_matrix, week_config = od_data_source.generate(args)

else:

    print("Reading OD..")
    od_matrices_by_hour, week_config, grid_config = od_data_source.load_norm()
    grid_matrix = get_grid_matrix_from_config(grid_config)

print(grid_matrix)

zone_ids = np.ravel(grid_matrix.values)

train_start_time = datetime.datetime(2023, 1, 1, 0, 0, 1)
train_end_time = train_start_time + datetime.timedelta(hours=args.n_hours[0])
test_start_time = train_end_time
test_end_time = test_start_time + datetime.timedelta(hours=args.n_hours[1])

if args.od_params[1] > 0:

    print("Generating trips..")

    train_booking_requests, test_booking_requests = generate_trips_from_od(
        args.city,
        od_matrices_by_hour,
        week_config,
        grid_matrix,
        zone_ids,
        od_data_source.distance_matrix,
        train_start_time,
        train_end_time,
        test_start_time,
        test_end_time,

    )
    print("Train trips shape:", train_booking_requests.shape)
    print("Test trips shape:", test_booking_requests.shape)

end = datetime.datetime.now()

print("Execution time [sec]: ", (end-start).total_seconds())
