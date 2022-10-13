import argparse
import datetime

from odysseus.city_data_manager.od_matrices.virtual_od.od_generator import generate_trips_from_od
from odysseus.city_data_manager.od_matrices.virtual_od.virtual_od_data_source import *

parser = argparse.ArgumentParser()

parser.add_argument(
    "-r", "--read", action="store_true",
    help="If "
)

parser.add_argument(
    "-c", "--city",
    help="specify city name"
)

parser.add_argument(
    "-d", "--data_source_id",
    help="specify data source id"
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
    nargs=1, metavar=('count', ),
    help="specify number of trips for a uniform OD matrix",
)

parser.set_defaults(
    read=False,
    city="my_city_2X2_2",
    data_source_id="my_data_source",
    week_slots_type="generic_day",
    day_slots_type="generic_hour",
    n_hours=(24, 24),
    grid_params=(2, 2, 500),
    od_params=("simple_cyclic", 1, ),
)

args = parser.parse_args()

od_data_source = VirtualODDataSource(args.city, args.data_source_id)

if not args.read:

    od_matrices_by_dayslots, od_matrices_by_hour, grid_matrix, week_config = od_data_source.generate(args)

else:

    od_matrices_by_hour, week_config, grid_config = od_data_source.load_norm()
    grid_matrix = get_grid_matrix_from_config(grid_config)

zone_ids = np.ravel(grid_matrix.values)

train_start_time = datetime.datetime(2023, 1, 1, 0, 0, 1)
train_end_time = train_start_time + datetime.timedelta(hours=args.n_hours[0])
test_start_time = train_end_time
test_end_time = test_start_time + datetime.timedelta(hours=args.n_hours[1])

if args.od_params[1] > 0:
    train_booking_requests, test_booking_requests = generate_trips_from_od(
        args.city,
        od_matrices_by_hour,
        week_config,
        grid_matrix,
        zone_ids,
        train_start_time,
        train_end_time,
        test_start_time,
        test_end_time,
    )
