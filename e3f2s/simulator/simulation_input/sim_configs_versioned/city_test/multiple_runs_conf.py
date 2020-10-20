import datetime
import numpy as np

sim_scenario_conf_grid = {

    "requests_rate_factor": [1],
    "n_vehicles_factor": [1],

    "time_estimation": [True],
    "queuing": [True],

    "alpha": [26],
    "beta": [100],
    "n_poles_n_vehicles_factor": [0.2],

    "hub": [False],
    "hub_zone_policy": [""],

    "distributed_cps": [True],
    "system_cps": [True],
    "cps_placement_policy": ["num_parkings"],
    "cps_zones_percentage": [0.01, 0.05, 0.1, 0.2],

    "battery_swap": [False],
    "avg_reach_time": [1],
    "avg_service_time": [1],

    "n_workers": [1000],
    "relocation": [False],

    "user_contribution": [False],
    "willingness": [0],

}
