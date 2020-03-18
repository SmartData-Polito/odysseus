import os
import sys
import datetime

import pandas as pd

from simulator.SingleRun.single_run import single_run
from MultipleRun.multiple_runs import multiple_runs

from simulator.utils.path_utils import create_output_folders

confs_dict = {}

from SimulationInput.confs.sim_general_conf import sim_general_conf

print(sim_general_conf)

from SimulationInput.confs.multiple_runs_conf import sim_scenario_conf_grid
confs_dict["multiple_runs"] = sim_scenario_conf_grid

from SimulationInput.confs.single_run_conf import sim_scenario_conf
confs_dict["single_run"] = sim_scenario_conf


n_cores = sys.argv[1]
city_name = sys.argv[2]
sim_run_mode = sys.argv[3]
sim_scenario_name = sys.argv[4]

print (datetime.datetime.now(), city_name, sim_scenario_name, "starting..")

create_output_folders(city_name, sim_scenario_name)
#run_model_validation(city_name)
#print (datetime.datetime.now(), city_name, "validation finished")

if sim_run_mode == "single_run":
    single_run((
        city_name,
        sim_general_conf,
        confs_dict[sim_run_mode],
        "traceB",
        sim_scenario_name
    ))
elif sim_run_mode == "multiple_runs":
    multiple_runs(
        city_name,
        "multiple_runs",
        sim_general_conf,
        confs_dict[sim_run_mode],
        int(n_cores),
        sim_scenario_name
    )

# plot_multiple_runs (city_name, sim_scenario_name)

print (datetime.datetime.now(), city_name, sim_scenario_name, "finished!")
