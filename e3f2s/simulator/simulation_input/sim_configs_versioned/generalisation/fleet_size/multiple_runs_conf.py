import datetime
import numpy as np

sim_scenario_conf_grid = {

    "n_requests": [100000, 500000, 1000000],
    "fleet_load_factor": np.arange(100, 10000, 50),

    "time_estimation": [True],
    "queuing": [True],

    "alpha_policy": ['auto'],
    "beta": [100],
    "n_poles_n_vehicles_factor": [0.2, 1],

    "hub": [False],
    "hub_zone_policy": [""],

    "distributed_cps": [True],
    "system_cps": [True],
    "cps_placement_policy": ["num_parkings"],
    "cps_zones_percentage": [0.2],

    "battery_swap": [False],
    "avg_reach_time": [0],
    "avg_service_time": [0],

    "n_workers": [1000],
    "relocation": [False],

    "user_contribution": [False],
    "willingness": [0],

}
