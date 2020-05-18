import os

simulator_path = os.path.dirname(__file__)

simulation_input_paths={
    'confs_target': os.path.join(simulator_path, 'simulation_input', 'confs_target.json'),
    'confs_versioned': os.path.join(simulator_path, 'simulation_input', 'confs_versioned'),
    'confs': os.path.join(simulator_path, 'simulation_input', 'confs')
}
