supply_model_config_grid = {

	# -> energy supply

	"year_energymix": ["2023"],

	# -> vehicle configuration

	"vehicle_model_name": ["Fiat 500e 2020"],
	"engine_type": ["electric"],
	"fuel_capacity": [37.3],
	"vehicle_efficiency": [5.263],

	# -> fleet size and initial placement

	"vehicles_config_mode": ["sim_config"],
	"vehicles_initial_placement": ["random_greedy"],
	"n_vehicles": [400],

	# -> charging

	"charging_config_mode": ["sim_config"],
	"distributed_cps": [True],
	"system_cps": [True],
	"profile_type": ["single_phase_2"],

	"stations_placement_config_mode": ["sim_config"],
	"tot_n_charging_poles": range(20, 21, 1),
	"n_charging_zones": [5, 10],
	"cps_placement_policy": ["num_parkings"],

	"charging_strategy": ["reactive"],
	"charging_relocation_strategy": ["closest_queueing"],
	"charging_return_strategy": ["last_destination"],
	"queuing": [True],
	"alpha_policy": ['manual'],
	"alpha": [30],
	"beta": [100],
	# "charging_duration": range(3600, 3600*7, 3600),

	"n_workers": [1],

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
