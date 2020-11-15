import datetime
import numpy as np

sim_scenario_conf_grid = {

    "requests_rate_factor": [5],
    "n_vehicles_factor": np.arange(1, 5, 0.1),

    "time_estimation": [True],
    "queuing": [True],

    "alpha_policy": ['auto'],
    "beta": [100],
    "tot_n_charging_poles": np.arange(30, 300, 5),

    "hub": [False],
    "hub_zone_policy": [""],

    "distributed_cps": [True],
    "system_cps": [True],
    "cps_placement_policy": ["num_parkings"],
    "cps_zones_percentage": [0.2],

    "battery_swap": [False],
    "avg_reach_time": [20],
    "avg_service_time": [0],

    "n_workers": [1000],
    "relocation": [False],

    "user_contribution": [False],
    "willingness": [0],

}
