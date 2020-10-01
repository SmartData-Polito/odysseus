sim_scenario_conf = {

	"requests_rate_factor": 1,
	"fleet_load_factor": 2,

	"time_estimation": True,
	"queuing": True,

	"alpha": 26,
	"beta": 100,

	"hub": False,
	"hub_zone_policy": "",
	"hub_zone": -1,

	"distributed_cps": True,
	"system_cps": True,
	"cps_placement_policy": "old_manual",
	"cps_zones": [386, 467, 468, 428],

	"battery_swap": False,
	"avg_reach_time": 1,
	"avg_service_time": 1,

	"n_workers": 1000,
	"relocation": False,

	"user_contribution": False,
	"willingness": 0,

}
