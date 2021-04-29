import datetime
import os
import json
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--n_cpus",
    help="specify max number of cpus to be used"
)

args = parser.parse_args()

from odysseus.simulator.simulation_input.sim_input_paths import simulation_input_paths

print(datetime.datetime.now())

with open(simulation_input_paths['sim_configs_target'], 'r') as my_file:
    data = my_file.read()
campaign_name = json.loads(data)['campaign_name']
conf_name = json.loads(data)['config_names'][0]

versioned_conf_path = os.path.join(
    simulation_input_paths["sim_configs_versioned"],
    campaign_name,
    conf_name
)
conf_path = versioned_conf_path


from odysseus.simulator.single_run.single_run import single_run
#from odysseus.simulator.multiple_runs.multiple_runs import multiple_runs
from odysseus.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid

from odysseus.simulator.simulation_input.sim_current_config.sim_general_conf import sim_general_conf_grid
from odysseus.simulator.simulation_input.sim_current_config.multiple_runs_conf import sim_scenario_conf_grid
from odysseus.simulator.simulation_input.sim_current_config.single_run_conf import sim_scenario_conf


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
        if args.n_cpus is not None:
            multiple_runs(
                sim_general_conf,
                confs_dict[sim_general_conf["sim_run_mode"]],
                sim_general_conf["sim_scenario_name"],
                n_cpus=int(args.n_cpus)
            )
        else:
            multiple_runs(
                sim_general_conf,
                confs_dict[sim_general_conf["sim_run_mode"]],
                sim_general_conf["sim_scenario_name"],
            )
