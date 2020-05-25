import os
import datetime
import multiprocessing as mp

import numpy as np
import pandas as pd

from simulator.data_structures.city import City
from simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid
from simulator.single_run.get_traceB_input import get_traceB_input
from simulator.single_run.get_eventG_input import get_eventG_input
from simulator.single_run.run_eventG_sim import get_eventG_sim_stats
from simulator.single_run.run_traceB_sim import get_traceB_sim_stats
from simulator.simulation_output.multiple_runs_plotter import EFFCS_MultipleRunsPlotter


def multiple_runs(sim_run_conf, sim_general_conf, sim_scenario_conf_grid, sim_scenario_name):

	city = sim_run_conf["city"]
	n_cores = sim_run_conf["n_cores"]
	sim_type = sim_run_conf["sim_technique"]

	model_general_conf_string = "_".join([str(v) for v in sim_general_conf.values()]).replace("'", "").replace(".", "d")
	model_scenario_conf_grid_string = "_".join([
		str(v) for v in sim_scenario_conf_grid.values()
	]).replace(" ", "-").replace("'", "").replace(".", "d").replace(",", "-").replace("[", "-").replace("]", "-")
	results_path = os.path.join(
		os.path.dirname(os.path.dirname(__file__)),
		"results",
		city,
		"multiple_runs",
		sim_scenario_name,
	)
	os.makedirs(results_path, exist_ok=True)

	print("Number of cores:", mp.cpu_count())
	with mp.Pool(mp.cpu_count()) as pool:

		city_obj = City(city, sim_run_conf["data_source_id"], sim_general_conf)
		sim_conf_grid = EFFCS_SimConfGrid(sim_scenario_conf_grid)

		pool_stats_list = []

		conf_tuples = []

		for sim_scenario_conf in sim_conf_grid.conf_list:
			conf_tuples += [(
				sim_general_conf,
				sim_scenario_conf,
				city_obj
			)]

		if sim_type == "eventG":

			sim_inputs = pool.map(get_eventG_input, conf_tuples)
			pool_stats_list += pool.map(get_eventG_sim_stats, sim_inputs)

		elif sim_type == "traceB":

			sim_inputs = pool.map(get_traceB_input, conf_tuples)
			pool_stats_list += pool.map(get_traceB_sim_stats, sim_inputs)

	sim_stats_df = pd.concat([sim_stats for sim_stats in pool_stats_list], axis=1, ignore_index=True).T

	sim_stats_df.to_csv(os.path.join(results_path, "sim_stats.csv"))
	pd.Series(sim_general_conf).to_csv(os.path.join(results_path, "sim_general_conf.csv"), header=True)
	pd.Series(sim_scenario_conf_grid).to_csv(os.path.join(results_path, "sim_scenario_conf_grid.csv"), header=True)

	sim_stats_df.to_pickle(os.path.join(results_path, "sim_stats.pickle"))
	pd.Series(sim_general_conf).to_pickle(os.path.join(results_path, "sim_general_conf.pickle"))
	pd.Series(sim_scenario_conf_grid).to_pickle(os.path.join(results_path, "sim_scenario_conf_grid.pickle"))

	# plotter = EFFCS_MultipleRunsPlotter(
	# 	city, sim_scenario_name, sim_general_conf, sim_scenario_conf_grid,
	# 	"alpha", "fraction_unsatisfied", "beta"
	# )
	# plotter.plot_x_y_param()
	#
	# plotter = EFFCS_MultipleRunsPlotter(
	# 	city, sim_scenario_name, sim_general_conf, sim_scenario_conf_grid,
	# 	"alpha", "fraction_not_same_zone_trips", "beta"
	# )
	# plotter.plot_x_y_param()
	#
	# plotter = EFFCS_MultipleRunsPlotter(
	# 	city, sim_scenario_name, sim_general_conf, sim_scenario_conf_grid,
	# 	"alpha", "fraction_no_close_cars", "beta"
	# )
	# plotter.plot_x_y_param()
	#
	# plotter = EFFCS_MultipleRunsPlotter(
	# 	city, sim_scenario_name, sim_general_conf, sim_scenario_conf_grid,
	# 	"alpha", "fraction_not_enough_energy", "beta"
	# )
	# plotter.plot_x_y_param()
