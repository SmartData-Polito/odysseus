supply_model_config_grid = {

	# -> energy supply

	"year_energymix": ["2023"],

	# -> vehicle configuration

	"vehicle_model_name": ["generic e-scooter"],
	"engine_type": ["electric"],
	"fuel_capacity": [0.425],
	"vehicle_efficiency": [1 / 0.011],

	# -> fleet size and initial placement

	"vehicles_config_mode": ["sim_config"],
	"vehicles_initial_placement": ["random_greedy"],
	"n_vehicles": list(range(1000, 11000, 1000)),

	# -> charging

	"charging_config_mode": ["sim_config"],
	"distributed_cps": [False],
	"system_cps": [False],
	"profile_type": ["single_phase_1"],

	"stations_placement_config_mode": ["sim_config"],
	"tot_n_charging_poles": [0],
	"n_charging_zones": [0],
	"cps_placement_policy": ["num_parkings"],

	"charging_strategy": ["reactive"],
	"charging_relocation_strategy": ["closest_free"],
	"charging_return_strategy": ["no_return"],
	"queuing": [True],

	"alpha_policy": ['auto'],
	# "alpha": [40],
	"beta": [100],
	# "charging_duration": range(3600, 3600*7, 3600),

	"n_workers": [1000],

	# -> battery swap

	"battery_swap": [True],
	"avg_reach_time": [30],
	"avg_service_time": [5],

	# -> relocation

	"relocation": [False],
	"relocation_strategy": ["proactive"],

	"relocation_technique": [
		frozenset({
			"start": "delta",
			"end": "delta",
			"window_width": 1,
		}.items())
	],

	"n_relocation_workers": [1],
	"avg_relocation_speed": [20],  # km/h
	"relocation_capacity": [30],
	"relocation_profitability_check": [False],
	"relocation_vehicle_consumption": [7],  # l/100km
	"diesel_price": [0.65],  # $/l (USA)
	"unlock_fee": [1],  # $
	"rent_fee": [0.15],  # $/min
	"avg_relocation_distance": [1],  # km
	"avg_trip_duration": [10],  # min

}
