import os

sim_input_path = os.path.dirname(__file__)

simulation_input_paths = {
    'sim_configs_target': os.path.join(sim_input_path, 'sim_configs_target.json'),
    'sim_configs_versioned': os.path.join(sim_input_path, 'sim_configs_versioned'),
}
