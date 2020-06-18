import datetime

sim_scenario_conf = {

    "requests_rate_factor": 1,
    "n_cars_factor": 1,

    "time_estimation": True,
    "queuing": True,
    "alpha": 25,
    "beta": 100,

    "hub": True,
    "hub_zone_policy": "num_parkings",
    "n_poles_n_cars_factor": 0.15,

    "relocation": False,
    "finite_workers": False,

    "distributed_cps": False,
    "cps_placement_policy": "num_parkings",
    "n_charging_poles": 20,
    "cps_zones_percentage": 0.1,

    "user_contribution": False,
    "system_cps": False,
    "willingness": 0.99,

}
