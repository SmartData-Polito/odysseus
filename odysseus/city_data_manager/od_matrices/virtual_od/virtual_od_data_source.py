import os
import json
import numpy as np

from odysseus.city_data_manager.od_matrices.virtual_od.od_generator import (
    generate_week_config, generate_hourly_od_count_dict, generate_od_from_week_config, root_data_path
)
from odysseus.city_data_manager.od_matrices.virtual_od.od_reader import get_grid_matrix_from_config, read_od_matrices


class VirtualODDataSource:

    """
    This abstract class is used to define virtual OD matrices without explicit geographical information.

    :param city_id: User-defined city name
    :type city_id: str
    :param data_source_id: User-defined data source id (might be useful to represent different scenarios)
    :type data_source_id: str
    """

    def __init__(self, city_name, data_source_id):

        self.city_name = city_name
        self.data_source_id = data_source_id
        self.data_type_id = "od_matrices"

    def generate(self, args):

        """
        This method is used to generate OD matrices depending on arguments provided from the command-line interface.

        :param args: Command line arguments
        :type args: parser.ArgumentParser()
        """

        week_config = generate_week_config(
            week_slots_type=args.week_slots_type,
            day_slots_type=args.day_slots_type,
        )
        base_path = os.path.join(root_data_path, args.city, "norm", "od_matrices", args.data_source_id)
        os.makedirs(base_path, exist_ok=True)

        with open(os.path.join(base_path, "week_config.json"), "w") as f:
            json.dump(week_config, f, indent=4)

        grid_config = {
            "cell_type": "square",
            "n_rows": args.grid_params[0],
            "n_cols": args.grid_params[1],
            "bin_side_length": args.grid_params[2]
        }

        with open(os.path.join(base_path, "grid_config.json"), "w") as f:
            json.dump(grid_config, f, indent=4)

        grid_matrix = get_grid_matrix_from_config(grid_config)
        zone_ids = np.ravel(grid_matrix.values)

        hourly_od_count_dict = generate_hourly_od_count_dict(
            week_config, zone_ids, args.od_params[0], count=args.od_params[1], exclude_zones=args.od_params[2]
        )

        od_matrices_by_dayslots, od_matrices_by_hour = generate_od_from_week_config(
            city_name=args.city,
            data_source_id=args.data_source_id,
            week_config=week_config,
            zone_ids=zone_ids,
            od_type="count",
            hourly_od_count_dict=hourly_od_count_dict
        )

        return od_matrices_by_dayslots, od_matrices_by_hour, grid_matrix, week_config

    def save_norm(self):
        pass

    def load_norm(self):
        od_matrices_by_hour, week_config, grid_config = read_od_matrices(self.city_name, self.data_source_id)
        return od_matrices_by_hour, week_config, grid_config

