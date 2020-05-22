import os
import json

from shutil import copy
from simulator.simulation_input.sim_input_paths import simulation_input_paths

with open(simulation_input_paths['sim_configs_target'], 'r') as my_file: data = my_file.read()
conf_name = json.loads(data)['config_name']

versioned_conf_path = os.path.join(
    simulation_input_paths["sim_configs_versioned"],
    conf_name
)
conf_path = simulation_input_paths['sim_configs']
os.makedirs(conf_path, exist_ok=True)
try:
    for f in os.listdir(versioned_conf_path):
        if os.path.isfile(os.path.join(versioned_conf_path, f)):
            copy(
                os.path.join(versioned_conf_path, f),
                os.path.join(conf_path)
            )
    #print('Configuration Loaded')

except FileNotFoundError:
    print('Error %s conf not present' % conf_path + f)
    exit()
