import os
import importlib.util


def check_create_path (path):
	os.makedirs(path, exist_ok=True)


def get_sim_configs_from_path (config_path, config_name, config_var_name):
	spec = importlib.util.spec_from_file_location(
		config_name, os.path.join(config_path, config_name + ".py")
	)
	current_config_module = importlib.util.module_from_spec(spec)
	print(os.path.join(config_path, config_name + ".py"))
	if os.path.exists(os.path.join(config_path, config_name + ".py")):
		spec.loader.exec_module(current_config_module)
		return getattr(current_config_module, config_var_name)
	else:
		return None