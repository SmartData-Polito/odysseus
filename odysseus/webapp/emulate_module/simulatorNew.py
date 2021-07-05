#"bre-cambiato"

import datetime
import os
import json

from shutil import copy
import shutil

from odysseus.simulator.simulation_input.sim_input_paths import simulation_input_paths

from odysseus.simulator.single_run.single_run import single_run
from odysseus.simulator.multiple_runs.multiple_runs import multiple_runs
from odysseus.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid
from odysseus.simulator.simulation_input.sim_current_config.sim_general_conf import sim_general_conf_grid
from odysseus.simulator.simulation_input.sim_current_config.multiple_runs_conf import sim_scenario_conf_grid
from odysseus.simulator.simulation_input.sim_current_config.single_run_conf import sim_scenario_conf


class Simulator:
    def __init__(self, config_dict):
        self.city = config_dict["city"]
        self.demandModelName = config_dict["demandModelName"]
        self.supplyModelName = config_dict["supplyModelName"]
        pass

    def run(self):

        print(datetime.datetime.now())
        shutil.rmtree(simulation_input_paths["sim_current_config"])

        with open(simulation_input_paths['sim_configs_target'], 'r') as my_file:
            data = my_file.read()
        campaign_name = json.loads(data)['campaign_name']
        conf_name = json.loads(data)['config_names'][0]

        versioned_conf_path = os.path.join(
            simulation_input_paths["sim_configs_versioned"],
            campaign_name,
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
