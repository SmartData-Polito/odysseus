supply_model_config_grid = {

	# -> energy supply

	"year_energymix": ["2023"],

	# -> vehicle configuration

	"engine_type": ["gasoline"],
	"fuel_capacity": [20],
	"consumption": [1],
	"n_seats": [5],
	"vehicle_model_name": ["my_vehicle"],

	# -> fleet size and initial placement

	"vehicles_config_mode": ["sim_config"],
	"n_vehicles": [1, 2, 3, 4],
	"vehicles_initial_placement": ["random_greedy"],

	# -> charging

	"charging_config_mode": ["sim_config"],

	"n_workers": [1],

	"distributed_cps": [True],
	"system_cps": [True],
	"profile_type": [""],

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
	"charging_return_strategy": ["last_destination"],
	"queuing": [True],
	"alpha_policy": ['manual'],
	"alpha": [20],
	"beta": [100],
	"charging_duration": range(0, 3600*24, 3600),

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
