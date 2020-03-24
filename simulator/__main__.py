import sys
import datetime

from simulator.SingleRun.single_run import single_run
from simulator.MultipleRun.multiple_runs import multiple_runs
from simulator.SimulationInput.EFFCS_SimConfGrid import EFFCS_SimConfGrid

confs_dict = {}

from simulator.SimulationInput.confs.sim_general_conf import sim_general_conf_grid

from simulator.SimulationInput.confs.multiple_runs_conf import sim_scenario_conf_grid
confs_dict["multiple_runs"] = sim_scenario_conf_grid

from simulator.SimulationInput.confs.single_run_conf import sim_scenario_conf
confs_dict["single_run"] = sim_scenario_conf


n_cores = sys.argv[1]
city_name = sys.argv[2]
sim_run_mode = sys.argv[3]
sim_scenario_name = sys.argv[4]

print (datetime.datetime.now(), city_name, sim_scenario_name, "starting..")

sim_general_conf_list = EFFCS_SimConfGrid(sim_general_conf_grid).conf_list

for sim_general_conf in sim_general_conf_list:
    print(sim_general_conf)
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
            "traceB",
            sim_scenario_name
        )

# plot_multiple_runs (city_name, sim_scenario_name)

print (datetime.datetime.now(), city_name, sim_scenario_name, "finished!")
