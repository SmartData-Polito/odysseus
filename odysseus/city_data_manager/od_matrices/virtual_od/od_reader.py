import json

from odysseus.path_config.path_config import *
from odysseus.utils.geospatial_utils import *


def read_od_matrices(
    city_name, data_source_id
):
    od_files_path = os.path.join(root_data_path, city_name, "norm", "od_matrices", data_source_id)
    od_matrices = dict()

    with open(os.path.join(od_files_path, "week_config.json"), "r") as f:
        week_config = json.load(f)
    with open(os.path.join(od_files_path, "grid_config.json"), "r") as f:
        grid_config = json.load(f)

    for week_slot in week_config["week_slots"]:
        print(week_slot)
        od_matrices[week_slot] = dict()
        for day_slot in week_config["day_slots"][week_slot]:
            print(day_slot)
            od_matrix = pd.read_csv(os.path.join(od_files_path, "_".join([week_slot, day_slot]) + ".csv"), index_col=0)
            for hour in week_config["day_slots"][week_slot][day_slot]:
                od_matrices[week_slot][hour] = od_matrix

    return od_matrices, week_config, grid_config

