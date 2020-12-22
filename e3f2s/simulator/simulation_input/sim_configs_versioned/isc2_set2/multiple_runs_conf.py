import datetime
import numpy as np

sim_scenario_conf_grid = {

    "requests_rate_factor": [1, 5],
    "n_vehicles_factor": np.arange(0.05, 1.5, 0.05),

    "engine_type": ["electric"],
    "profile_type": ["single_phase_1"],  # works only if engine_type = electric
    "vehicle_model_name": ["Smart fortwo Electric Drive 2018"],
    "country_energymix": ["Italy"],
    "year_energymix": ["2018"],

    "time_estimation": [True],
    "queuing": [True],

    "alpha_policy": ['auto'],
    "beta": [100],
    "tot_n_charging_poles": np.arange(1, 301, 10),

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

    "charging_strategy": ["reactive"],
    "charging_relocation_strategy": ["closest_free"],
    "scooter_relocation": [False]

}
