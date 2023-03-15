import datetime

from odysseus.city_data_manager.od_matrices.virtual_od.od_to_trips import *

from odysseus.demand_modelling.demand_model import *
from odysseus.utils.time_utils import *

from odysseus.city_data_manager.od_matrices.virtual_od.od_to_trips import generate_booking_requests_list


class ODmatricesDemandModel(DemandModel):

    def __init__(
            self,
            city_name,
            data_source_id,
            demand_model_config,
            grid_crs
    ):
        super(ODmatricesDemandModel, self).__init__(
            city_name, data_source_id, demand_model_config, grid_crs
        )

    def fit_model(self):
        with open(os.path.join(self.city_scenario_path, "od_matrices.pickle"), "rb") as f:
            self.od_matrices = pickle.load(f)
        with open(os.path.join(self.city_scenario_path, "week_config.json"), "r") as f:
            self.week_config = json.load(f)

    def generate_booking_requests_sim(
            self,
            start_datetime,
            requests_rate_factor,
            avg_speed_kmh_mean,
            max_duration,
            fixed_driving_distance
    ):

        return generate_booking_requests_list(
            self.od_matrices, self.week_config, self.distance_matrix, start_datetime,
            start_datetime + datetime.timedelta(hours=1),
            requests_rate_factor,
            avg_speed_kmh_mean,
            max_duration,
            fixed_driving_distance
        )

    def save_results(self):
        self.save_config()

