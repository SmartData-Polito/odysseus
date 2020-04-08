import datetime
import numpy as np

sim_scenario_conf_grid = {

    "requests_rate_factor": [1],
    "n_cars_factor": [1],

    "time_estimation": [True],
    "queuing": [True],

    "alpha": [40],
    "beta": [100],
    "n_poles_n_cars_factor": [0.1],

    "hub": [False],
    "hub_zone_policy": [""],

    "distributed_cps": [False],
    "cps_placement_policy": [""],
    "cps_zones_percentage": [0.1],
    "user_contribution": [False],
    "system_cps": [False],
    "willingness": [0],

    "battery_swap": [True],
    "battery_swap_service_time": [30, 60, 90, 120],
    "n_workers": [1000],

    "relocation": [False],

}
