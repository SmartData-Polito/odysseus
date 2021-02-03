import datetime
import numpy as np

sim_scenario_conf_grid = {

    "n_requests": [10 ** 5],
    "n_vehicles": [400],##np.arange(1, 400, 6),
    "engine_type": ["electric"],
    "profile_type": ["three_phase_3"], # works only if engine_type = electric
    "vehicle_model_name": ["VW e-Golf 2018"],
    "country_energymix": ["Italy"],
    "year_energymix": ["2018"],

    "time_estimation": [True],
    "queuing": [True],

    "alpha_policy": ['auto'],
    "beta": [100],

    #"n_poles_n_vehicles_factor": np.arange(0.01, 0.2, 0.01),
    "tot_n_charging_poles": [200],#np.arange(1, 200, 3),#

    "hub": [False],
    "hub_zone_policy": [""],

    "distributed_cps": [True],
    "system_cps": [True],
    "cps_placement_policy": ["num_parkings"],
    "cps_zones_percentage": [0.2],

    "battery_swap": [False],
    "avg_reach_time": [20],
    "avg_service_time": [0],

    "n_workers":np.arange(1, 20, 1),# #[1000],
    "relocation": [False],

    "user_contribution": [False],
    "willingness": [0],
    
    "charging_strategy": ["reactive"],
	"charging_relocation_strategy": ["closest_free"], #closest_free/random/closest_queueing
    
    "number of workers": [1000],

	"scooter_relocation": [False],
	"scooter_relocation_strategy": [""],

	"vehicle_relocation": [False],
	"vehicle_relocation_strategy": ["magic_relocation"]

}
