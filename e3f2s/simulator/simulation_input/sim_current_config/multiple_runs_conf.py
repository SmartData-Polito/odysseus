import datetime
import numpy as np

sim_scenario_conf_grid = {

    "requests_rate_factor": [1],
    "n_vehicles_factor": np.arange(0.1, 2, 0.1),

    "time_estimation": [True],
    "queuing": [True],

    "alpha": [20],
    "beta": [100],
    "n_poles_n_vehicles_factor": [1],

    "hub": [False],
    "hub_zone_policy": [""],

    "distributed_cps": [False],
    "cps_placement_policy": [""],
    "cps_zones_percentage": [0.1],
    "system_cps": [False],

    "battery_swap": [True],
    "avg_reach_time": [5],
    "avg_service_time": [5],

    "n_workers": [100],
    "relocation": [False],

    "user_contribution": [False],
    "willingness": [0],

}