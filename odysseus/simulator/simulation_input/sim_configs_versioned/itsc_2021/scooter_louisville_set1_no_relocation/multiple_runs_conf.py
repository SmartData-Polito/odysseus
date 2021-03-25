import numpy as np

sim_scenario_conf_grid = {

    "n_vehicles": [850],

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
    "relocation_capacity": [30],
    "relocation_vehicle_consumption": [7],  # l/100km
    "diesel_price": [0.65],  # $/l (USA)
    "unlock_fee": [1],  # $
    "rent_fee": [0.15],  # $/min
    "avg_relocation_distance": [1],  # km
    "avg_trip_duration": [10],  # min

    "engine_type": ["electric"],
    "vehicle_model_name": ["generic e-scooter"],
}
