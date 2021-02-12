sim_scenario_conf = {

    "n_requests": 100000,
    "fleet_load_factor": 100000/1000,

    "time_estimation": True,
    "queuing": True,

    "alpha_policy": 'auto',

    "beta": 100,
    "n_poles_n_vehicles_factor": 1,

    "hub_zone_policy": "num_parkings",
    "hub": False,

    "cps_placement_policy": "num_parkings",
    "distributed_cps": False,
    "system_cps": False,
    "cps_zones_percentage": 0.2,

    "battery_swap": True,
    "avg_reach_time": 30,
    "avg_service_time": 5,

    "n_workers": 12,
    "relocation": False,

    "user_contribution": False,
    "willingness": 0,

    "charging_strategy": "reactive",
    "charging_relocation_strategy": "closest_free",  # closest_free/random/closest_queueing

    "number of workers": 1000,

    "scooter_relocation": True,
    "scooter_relocation_strategy": "only_scheduled",
    "scooter_relocation_technique": frozenset({
        "start": "aggregation",
        "start_demand_weight": 0.9,
        "start_vehicles_factor": 1,
        "start_window_width": 2,
        "end": "kde_sampling",
        "end_demand_weight": 0.9,
        "end_vehicles_factor": 1,
        "end_window_width": 2,
    }.items()),
    "scooter_relocation_scheduling": True,
    "scooter_scheduled_relocation_triggers": frozenset({
        "post_charge": False,
        "post_trip": False,
        "post_schedule_gen": True,
    }.items()),

    "n_relocation_workers": 12,
    "avg_relocation_speed": 20,  # km/h

    "vehicle_relocation": False,
    "vehicle_relocation_scheduling": False,

    "engine_type": "electric",
    "vehicle_model_name": "generic e-scooter",
    "country_energymix": "Italy",
    "year_energymix": "2018",
}
