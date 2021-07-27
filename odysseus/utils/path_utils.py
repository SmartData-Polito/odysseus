import os
import importlib.util


def check_create_path (path):
	os.makedirs(path, exist_ok=True)


def get_sim_configs_from_path (config_path, config_name, config_var_name):
	spec = importlib.util.spec_from_file_location(
		config_name, os.path.join(config_path, config_name + ".py")
	)
	current_config_module = importlib.util.module_from_spec(spec)
	if os.path.exists(os.path.join(config_path, config_name + ".py")):
		spec.loader.exec_module(current_config_module)
		return getattr(current_config_module, config_var_name)
	else:
		return None


def get_output_path(output_folder_name, city, sim_scenario_name, run_mode, conf_id=None):
	if run_mode == "single_run":
		results_path = os.path.join(
			os.path.dirname(os.path.dirname(__file__)),
			output_folder_name,
			city,
			run_mode,
			sim_scenario_name,
			str(conf_id)
		)
	elif run_mode == "multiple_runs":
		results_path = os.path.join(
			os.path.dirname(os.path.dirname(__file__)),
			output_folder_name,
			city,
			run_mode,
			sim_scenario_name,
		)
	os.makedirs(results_path, exist_ok=True)
	return results_path
