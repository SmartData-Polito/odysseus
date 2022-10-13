supply_model_conf_grid = {

	"n_vehicles_factor": [1],
	"engine_type": ["electric"],
	"profile_type": ["wall_plug"],
	"vehicle_model_name": ["generic e-scooter"],

	"year_energymix": ["2018"],

	"alpha_policy": ['auto'],
	"beta": [100],
	"n_poles_n_vehicles_factor": [0.2],

	"cps_placement_policy": [""],
	"distributed_cps": [False],
	"system_cps": [False],
	"cps_zones_percentage": [0],

	"battery_swap": [True],
	"avg_reach_time": [20],
	"avg_service_time": [0],

	"n_workers": [12],
	"relocation": [False],

	"charging_strategy": ["reactive"],
	"charging_relocation_strategy": ["closest_free"],
	"queuing": [True],

	"scooter_relocation": [False],
	"scooter_relocation_strategy": ["magic_relocation"],
	"scooter_relocation_scheduling": [False],
	"scooter_relocation_technique": [frozenset({
			"start": "aggregation",
			"start_demand_weight": 0.9,
			"start_vehicles_factor": 1,
			"end": "kde_sampling",
			"end_demand_weight": 0.9,
			"end_vehicles_factor": 1,
		}.items())],
	"scooter_scheduled_relocation_triggers": [frozenset({
			"post_charge": False,
			"post_trip": True,
		}.items())],

	"vehicle_relocation": [False],
	"vehicle_relocation_strategy": ["only_scheduling"],
	"vehicle_relocation_scheduling": [False],
	"vehicle_relocation_technique": [frozenset({
			"start": "aggregation",
			"end": "kde_sampling",
		}.items())],
	"vehicle_scheduled_relocation_triggers": [frozenset({
		"post_trip": True,
	}.items())],

	"n_relocation_workers": [12],
	"avg_relocation_speed": [20]  # km/h

}
