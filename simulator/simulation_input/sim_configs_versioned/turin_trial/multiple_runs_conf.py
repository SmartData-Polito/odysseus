import datetime
import numpy as np

sim_scenario_conf_grid = {

    "requests_rate_factor": [1],
    "n_vehicles_factor": [0.5, 0.625],

    "time_estimation": [True],
    "queuing": [True],

    "alpha": [40],
    "beta": [100],
    "n_poles_n_vehicles_factor": [0.1],

    "hub": [False],
    "hub_zone_policy": [""],

    "distributed_cps": [True],
    "system_cps": [True],
    "cps_placement_policy": ["num_parkings"],
    "cps_zones_percentage": [0.1],

    "battery_swap": [False],
    "avg_reach_time": [0],
    "avg_service_time": [0],

    "n_workers": [100],
    "relocation": [False],

    "user_contribution": [False],
    "willingness": [0],

}
