import os
import sys
import datetime

import pandas as pd

from Loading.create_input_pickles import create_input_pickles
from ModelValidation.model_validation import run_model_validation
from SingleRun.single_run import single_run
from MultipleRun.multiple_runs import multiple_runs
from SimulationOutput.EFFCS_MultipleRunsPlotter import plot_multiple_runs

from utils.path_utils import create_output_folders

confs_dict = {}

from SimulationInput.confs.sim_general_conf import sim_general_conf

from SimulationInput.confs.only_hub_conf import sim_scenario_conf_grid
confs_dict["only_hub"] = sim_scenario_conf_grid

from SimulationInput.confs.only_hub_np_w_conf import sim_scenario_conf_grid
confs_dict["only_hub_np_w"] = sim_scenario_conf_grid

from SimulationInput.confs.only_hub_alpha_beta_conf import sim_scenario_conf_grid
confs_dict["only_hub_alpha_beta"] = sim_scenario_conf_grid

from SimulationInput.confs.only_cps_conf import sim_scenario_conf_grid
confs_dict["only_cps"] = sim_scenario_conf_grid

from SimulationInput.confs.only_cps_np_w_conf import sim_scenario_conf_grid
confs_dict["only_cps_np_w"] = sim_scenario_conf_grid

from SimulationInput.confs.only_cps_alpha_beta_conf import sim_scenario_conf_grid
confs_dict["only_cps_alpha_beta"] = sim_scenario_conf_grid

from SimulationInput.confs.hub_cps_conf import sim_scenario_conf_grid
confs_dict["hub_cps"] = sim_scenario_conf_grid

from SimulationInput.confs.multiple_runs_conf import sim_scenario_conf_grid
confs_dict["trial"] = sim_scenario_conf_grid

from SimulationInput.confs.single_run_conf import sim_scenario_conf
confs_dict["single_run"] = sim_scenario_conf


n_cores = sys.argv[1]
city_name = sys.argv[2]
sim_scenario_name = sys.argv[3]

print (datetime.datetime.now(), city_name, sim_scenario_name, "starting..")

#create_output_folders(city_name, sim_scenario_name)
#create_input_pickles(city_name, [9, 10], 500)
#run_model_validation(city_name)
#print (datetime.datetime.now(), city_name, "validation finished")

if sim_scenario_name == "single_run":
    single_run((
        city_name,
        sim_general_conf,
        confs_dict["single_run"],
        "eventG",
        "only_hub"
    ))
else:
    multiple_runs(
        city_name,
        "multiple_runs",
        sim_general_conf,
        confs_dict[sim_scenario_name],
        int(n_cores),
        sim_scenario_name
    )

# plot_multiple_runs (city_name, sim_scenario_name)

print (datetime.datetime.now(), city_name, sim_scenario_name, "finished!")
