supply_model_config_grid = {

	# -> energy supply

	"year_energymix": ["2023"],

	# -> vehicle configuration

	"engine_type": ["gasoline"],
	"fuel_capacity": [5],
	"vehicle_efficiency": [10000],
	"n_seats": [5],
	"vehicle_model_name": ["my_vehicle"],

	# -> fleet size and initial placement

	"vehicles_config_mode": ["vehicles_zones"],
	# "n_vehicles": [1, 2, 3, 4],
	# "vehicles_initial_placement": ["random_greedy"],
	"vehicles_zones": [
		frozenset({0: 0}.items()),
		frozenset({0: 0, 1: 1}.items()),
		frozenset({0: 0, 1: 1, 2: 2}.items()),
		frozenset({0: 0, 1: 1, 2: 2, 3: 3}.items())
	],

	# -> charging

	"charging_config_mode": ["sim_config"],

	"n_workers": [1],

	"distributed_cps": [False],
	"system_cps": [False],
	"profile_type": [""],

	"stations_placement_config_mode": ["sim_config"],
	"cps_placement_policy": ["uniform"],
	"tot_n_charging_poles": [0],
	"n_charging_zones": [0],
	"charging_strategy": ["reactive"],
	"charging_relocation_strategy": ["closest_queueing"],
	"queuing": [True],
	"alpha_policy": ['auto'],
	# "alpha": [20],
	"beta": [100],

	# -> battery swap

	"battery_swap": [False],
	"avg_reach_time": [0],
	"avg_service_time": [0],

	# -> relocation

	"relocation": [False],
	"relocation_strategy": [""],

	"relocation_technique": [frozenset({})],

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
