supply_model_config_grid = {

	# -> energy supply

	"engine_type": ["gasoline"],
	"year_energymix": ["2023"],

	# -> vehicles

	"vehicles_config_mode": ["vehicles_zones"],
	"vehicle_model_name": ["VW Golf 7 1.0 TSI 2018"],
	# "vehicles_initial_placement": ["random_greedy"],
	"vehicles_zones": [
		frozenset(
			{
				0: 0,
			}.items()
		)
	],

	# -> charging

	"stations_config_mode": ["sim_config"],

	"distributed_cps": [True],
	"system_cps": [True],
	"profile_type": [""],

	"charging_config_mode": ["sim_config"],
	"cps_placement_policy": ["uniform"],
	"tot_n_charging_poles": [9],
	"n_charging_zones": [9],
	"charging_strategy": ["reactive"],
	"charging_relocation_strategy": ["closest_queueing"],
	"queuing": [True],

	"alpha_policy": ['auto'],
	# "alpha": [20],
	"beta": [100],

	# -> battery swap

	"n_workers": [12],
	"battery_swap": [False],
	"avg_reach_time": [0],
	"avg_service_time": [0],

	# -> relocation

	"relocation": [False],
	"relocation_strategy": [""],

	"relocation_technique": [frozenset({})],

	# "relocation_technique": [frozenset({
	# 		"start": "delta",
	# 		"end": "delta",
	# 		"window_width": 1,
	# 	}.items())],

	"n_relocation_workers": [1],
	"avg_relocation_speed": [20],  # km/h
	"relocation_capacity": [1],
	"relocation_profitability_check": [False],
	"relocation_vehicle_consumption": [7],  # l/100km
	"diesel_price": [0.65],  # $/l (USA)
	"unlock_fee": [1],  # $
	"rent_fee": [0.15],  # $/min
	"avg_relocation_distance": [1],  # km
	"avg_trip_duration": [10],  # min

}
