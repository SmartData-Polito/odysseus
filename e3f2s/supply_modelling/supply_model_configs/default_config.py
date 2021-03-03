supply_model_configs_grid = {

    "city": ["Torino", "Milano", "Vancouver"],

    "data_source_id": ["big_data_db"],

    "n_vehicles": [500],
    "engine_type": ["electric"],
    "vehicle_model_name": ["Smart fortwo Electric Drive 2018"],

    "distributed_cps": [True],
    "cps_placement_policy": ["num_parkings"],
    "profile_type": ["single_phase_1"],  # works only if engine_type = electric

    "country_energymix": ["Italy"],
    "year_energymix": ["2018"],

}
