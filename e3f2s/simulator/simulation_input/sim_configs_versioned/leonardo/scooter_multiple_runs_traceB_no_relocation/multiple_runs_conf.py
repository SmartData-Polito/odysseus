import numpy as np

sim_scenario_conf_grid = {

    "n_requests": [1000000],
    "fleet_load_factor": 1000000 / np.arange(100, 2001, 100),

    "time_estimation": [True],
    "queuing": [True],

    "alpha_policy": ['auto'],
    "beta": [100],

    "n_poles_n_vehicles_factor": [1],

    "hub": [False],
    "hub_zone_policy": [""],

    "distributed_cps": [False],
    "system_cps": [False],
    "cps_placement_policy": ["num_parkings"],
    "cps_zones_percentage": [0.2],

    "battery_swap": [True],
    "avg_reach_time": [30],
    "avg_service_time": [5],

    "n_workers": [1000],
    "relocation": [False],

    "user_contribution": [False],
    "willingness": [0],

    "charging_strategy": ["reactive"],
    "charging_relocation_strategy": ["closest_free"],  # closest_free/random/closest_queueing

    "number of workers": [1000],

    "scooter_relocation": [False],
    "scooter_relocation_strategy": ["no_relocation"],

    "vehicle_relocation": [False],
    "vehicle_relocation_scheduling": [False],

    "n_relocation_workers": [12],
    "avg_relocation_speed": [20],  # km/h

    "engine_type": ["electric"],
    "vehicle_model_name": ["generic e-scooter"],
    "year_energymix": ["2019"],
}
