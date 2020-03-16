import os

def check_create_path (path):
	if not os.path.exists(path):
		os.mkdir(path)


def create_output_folders (city_name, sim_scenario_name):

	results_path = os.path.join \
		(os.getcwd(), "Results")
	if not os.path.exists(results_path):
		os.mkdir(results_path)

	results_path = os.path.join \
		(os.getcwd(), "Figures")
	if not os.path.exists(results_path):
		os.mkdir(results_path)

	results_path = os.path.join \
		(os.getcwd(), "Results", city_name)
	if not os.path.exists(results_path):
		os.mkdir(results_path)

	results_path = os.path.join \
		(os.getcwd(), "Figures", city_name)
	if not os.path.exists(results_path):
		os.mkdir(results_path)


	results_path = os.path.join \
		(os.getcwd(), "Figures", city_name, "multiple_runs")
	if not os.path.exists(results_path):
		os.mkdir(results_path)

	results_path = os.path.join \
		(os.getcwd(), "Figures", city_name, "multiple_runs", sim_scenario_name)
	if not os.path.exists(results_path):
		os.mkdir(results_path)
