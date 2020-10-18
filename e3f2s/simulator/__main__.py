import datetime

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
