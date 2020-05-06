import sys
import datetime
import argparse

from simulator.single_run.single_run import single_run
from simulator.multiple_runs.multiple_runs import multiple_runs
from simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid

from simulator.simulation_input.confs.sim_run_conf import sim_run_conf
from simulator.simulation_input.confs.sim_general_conf import sim_general_conf_grid
from simulator.simulation_input.confs.multiple_runs_conf import sim_scenario_conf_grid
from simulator.simulation_input.confs.single_run_conf import sim_scenario_conf

confs_dict = {}
confs_dict["multiple_runs"] = sim_scenario_conf_grid
confs_dict["single_run"] = sim_scenario_conf

n_cores = sim_run_conf["n_cores"]
city_name = sim_run_conf["city"]
sim_run_mode = sim_run_conf["sim_run_mode"]
sim_scenario_name = sim_run_conf["sim_scenario_name"]

print (datetime.datetime.now(), city_name, sim_scenario_name, "starting..")

sim_general_conf_list = EFFCS_SimConfGrid(sim_general_conf_grid).conf_list

for sim_general_conf in sim_general_conf_list:
    print(sim_general_conf)
    if sim_run_mode == "single_run":
        single_run((
            sim_run_conf,
            sim_general_conf,
            confs_dict[sim_run_mode],
            "traceB",
            sim_scenario_name
        ))
    elif sim_run_mode == "multiple_runs":
        multiple_runs(
            sim_run_conf,
            "multiple_runs",
            sim_general_conf,
            confs_dict[sim_run_mode],
            "traceB",
            sim_scenario_name
        )

# plot_multiple_runs (city_name, sim_scenario_name)

print (datetime.datetime.now(), city_name, sim_scenario_name, "finished!")
