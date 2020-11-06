import datetime
import pickle
import os
import json

from shutil import copy

from e3f2s.simulator.simulation_input.sim_input_paths import simulation_input_paths

print(datetime.datetime.now())

with open(simulation_input_paths['sim_configs_target'], 'r') as my_file:
    data = my_file.read()
conf_name = json.loads(data)['config_names'][0]

versioned_conf_path = os.path.join(
    simulation_input_paths["sim_configs_versioned"],
    conf_name
)
conf_path = simulation_input_paths['sim_current_config']
os.makedirs(conf_path, exist_ok=True)

try:
    for f in os.listdir(versioned_conf_path):
        if os.path.isfile(os.path.join(versioned_conf_path, f)):
            copy(
                os.path.join(versioned_conf_path, f),
                os.path.join(conf_path)
            )

except FileNotFoundError:
    print('Error %s conf not present' % conf_path + f)
    exit()

import pandas as pd

from e3f2s.demand_modelling.city import City

from e3f2s.simulator.single_run.single_run import single_run
from e3f2s.simulator.multiple_runs.multiple_runs import multiple_runs
from e3f2s.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid

from e3f2s.simulator.simulation_input.sim_current_config.sim_general_conf import sim_general_conf_grid
from e3f2s.simulator.simulation_input.sim_current_config.multiple_runs_conf import sim_scenario_conf_grid
from e3f2s.simulator.simulation_input.sim_current_config.single_run_conf import sim_scenario_conf


confs_dict = {}
confs_dict["multiple_runs"] = sim_scenario_conf_grid
confs_dict["single_run"] = sim_scenario_conf

sim_general_conf_list = EFFCS_SimConfGrid(sim_general_conf_grid).conf_list
for sim_general_conf in sim_general_conf_list:
    sim_run_mode = sim_general_conf["sim_run_mode"]
    print(sim_general_conf)

    demand_model_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "demand_modelling",
        "demand_models",
        sim_general_conf["city"],
    )
    os.makedirs(demand_model_path, exist_ok=True)

    if not os.path.exists(os.path.join(demand_model_path, "city_obj.pickle")):
        city_obj = City(sim_general_conf["city"], sim_general_conf)
        pickle.dump(
            city_obj,
            open(os.path.join(demand_model_path, "city_obj.pickle"), "wb")
        )
        city_obj.grid_matrix.to_pickle(
            os.path.join(demand_model_path, "grid_matrix.pickle")
        )
        city_obj.grid_matrix.to_csv(
            os.path.join(demand_model_path, "grid_matrix.csv")
        )
        city_obj.grid.to_pickle(
            os.path.join(demand_model_path, "grid.pickle")
        )
        city_obj.grid.to_csv(
            os.path.join(demand_model_path, "grid.csv")
        )
        pd.DataFrame(city_obj.neighbors_dict).to_pickle(
            os.path.join(demand_model_path, "neighbors_dict.pickle")
        )
        city_obj.bookings.to_csv(os.path.join(demand_model_path, "bookings.csv"))

    if sim_run_mode == "single_run":
        single_run((
            sim_general_conf,
            confs_dict[sim_general_conf["sim_run_mode"]],
            sim_general_conf["sim_scenario_name"]
        ))
    elif sim_run_mode == "multiple_runs":
        multiple_runs(
            sim_general_conf,
            confs_dict[sim_general_conf["sim_run_mode"]],
            sim_general_conf["sim_scenario_name"]
        )
