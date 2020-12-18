sim_scenario_conf = {

	"n_requests": 10**5,
	"n_vehicles": 200,

	"time_estimation": True,
	"queuing": True,

	"alpha_policy": 'auto',

	"beta": 100,
	"n_poles_n_vehicles_factor": 0.06,

	"hub_zone_policy": "num_parkings",
	"hub": False,

	"cps_placement_policy": "num_parkings",
	"distributed_cps": True,
	"system_cps": True,
	"cps_zones_percentage": 0.2,

	"battery_swap": False,
	"avg_reach_time": 20,
	"avg_service_time": 0,

	"n_workers": 1000,
	"relocation": False,

	"user_contribution": False,
	"willingness": 0,

	"charging_strategy": "reactive",
	"charging_relocation_strategy": "closest_free", #closest_free/random/closest_queueing
<<<<<<< e159f49632e3e0c5006fce5fc2b99f9ab0de2157
=======


	"vehicle_relocation": True,
	"vehicle_relocation_strategy": "magic_relocation"


>>>>>>> add magic relocations to vehicle

}
