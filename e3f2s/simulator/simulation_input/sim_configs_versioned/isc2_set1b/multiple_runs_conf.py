import datetime
import numpy as np


sim_scenario_conf_grid = {

    "requests_rate_factor": np.arange(1, 4, 1),
    "n_vehicles_factor": np.arange(1, 4, 1),

    "time_estimation": [True],
    "queuing": [True],

    "alpha_policy": ['auto'],
    "beta": [100],

    "n_poles_n_vehicles_factor": [0.1],

    "hub": [False],
    "hub_zone_policy": [""],

    "distributed_cps": [True],
    "system_cps": [True],
    "cps_placement_policy": ["num_parkings"],
    "n_charging_zones": [1] + list(np.arange(2, 60, 3)),

    "battery_swap": [False],
    "avg_reach_time": [20],
    "avg_service_time": [0],

    "n_workers": [1000],
    "relocation": [False],

    "user_contribution": [False],
    "willingness": [0],

}
