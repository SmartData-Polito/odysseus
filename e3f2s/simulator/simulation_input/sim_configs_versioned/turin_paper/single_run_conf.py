sim_scenario_conf = {

	"requests_rate_factor": 1,
	"fleet_load_factor": 2,

	"time_estimation": True,
	"queuing": True,

	"alpha": 26,
	"beta": 100,
	"n_poles_n_vehicles_factor": 0.2,

	"hub": True,
	"hub_zone_policy": "manual",
	"hub_zone": 360,

	"distributed_cps": False,
	"system_cps": False,
	"cps_placement_policy": "",
	"cps_zones_percentage": 0,

	"battery_swap": False,
	"avg_reach_time": 1,
	"avg_service_time": 1,

	"n_workers": 1000,
	"relocation": False,

	"user_contribution": False,
	"willingness": 0,

}
