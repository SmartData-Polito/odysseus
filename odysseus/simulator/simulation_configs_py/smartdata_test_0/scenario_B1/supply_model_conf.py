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

	"charging_config_mode": ["sim_config"],

	"n_workers": [1],

	"distributed_cps": [True],
	"system_cps": [True],
	"profile_type": ["fixed_duration"],
	"fixed_charging_duration": [60*60*3],

	"stations_placement_config_mode": ["n_charging_poles_by_zone"],
	"n_charging_poles_by_zone": [
		frozenset(
			{
				4: 1,
			}.items()
		)
	],

	"charging_strategy": ["reactive"],
	"charging_relocation_strategy": ["closest_queueing"],
	"queuing": [True],

	"alpha_policy": ['sim_config'],
	"alpha": [80],
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
