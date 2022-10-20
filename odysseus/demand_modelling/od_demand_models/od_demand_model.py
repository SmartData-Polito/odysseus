import datetime

from odysseus.demand_modelling.demand_model import *
from odysseus.utils.time_utils import *


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
        with open(os.path.join(self.city_scenario_path, "od_matrices.pickle"), "r") as f:
            self.od_matrices = pickle.load(f)
