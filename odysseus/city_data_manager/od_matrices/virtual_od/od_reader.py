import json

from odysseus.path_config.path_config import *

from odysseus.city_data_manager.od_matrices.od_to_trips import *


def read_od_matrices(
    city_name, data_source_id
):
    od_files_path = os.path.join(root_data_path, city_name, "norm", "od_matrices", data_source_id)
    od_matrices = dict()

    with open(os.path.join(od_files_path, "week_config.json"), "r") as f:
        week_config = json.load(f)

    for week_slot in week_config["week_slots"]:
        print(week_slot)
        od_matrices[week_slot] = dict()
        for day_slot in week_config["day_slots"][week_slot]:
            print(day_slot)
            od_matrix = pd.read_csv(os.path.join(od_files_path, "_".join([week_slot, day_slot]) + ".csv"), index_col=0)
            for hour in week_config["day_slots"][week_slot][day_slot]:
                od_matrices[week_slot][hour] = od_matrix

    return od_matrices


od_matrices_ = read_od_matrices("my_city_3X3_to_read", "my_data_source")

grid_matrix = get_city_grid_as_matrix(
    (0, 0, 1500, 1500),
    500,
    "dummy_crs"
)

zone_ids = np.ravel(grid_matrix.values)

generate_trips_from_od(
    "my_city_3X3_to_read",
    od_matrices_,
    grid_matrix,
    zone_ids,
    datetime.datetime(2023, 1, 1, 0, 0, 1),
    datetime.datetime(2023, 1, 8, 0, 0, 1),
    datetime.datetime(2023, 1, 8, 0, 0, 1),
    datetime.datetime(2023, 1, 15, 0, 0, 1),
)

