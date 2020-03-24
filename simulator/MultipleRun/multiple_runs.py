import os
import datetime
import multiprocessing as mp

import numpy as np
import pandas as pd

from simulator.DataStructures.City import City
from simulator.SimulationInput.EFFCS_SimConfGrid import EFFCS_SimConfGrid
from simulator.SingleRun.get_traceB_input import get_traceB_input
from simulator.SingleRun.get_eventG_input import get_eventG_input
from simulator.SingleRun.run_eventG_sim import get_eventG_sim_stats
from simulator.SingleRun.run_traceB_sim import get_traceB_sim_stats
from simulator.SimulationOutput.EFFCS_MultipleRunsPlotter import EFFCS_MultipleRunsPlotter


def multiple_runs(city, sim_run_mode, sim_general_conf, sim_scenario_conf_grid, n_cores, sim_type, sim_scenario_name):

	model_general_conf_string = "_".join([str(v) for v in sim_general_conf.values()]).replace("'", "").replace(".", "-")
	model_scenario_conf_grid_string = "_".join([
		str(v) for v in sim_scenario_conf_grid.values()
	]).replace(" ", "-").replace("'", "").replace(".", "d").replace(",", "-").replace("[", "-").replace("]", "-")
	results_path = os.path.join(
		os.path.dirname(os.path.dirname(__file__)),
		"Results",
		city,
		sim_run_mode,
		sim_scenario_name,
		model_general_conf_string,
		model_scenario_conf_grid_string
	)
	os.makedirs(results_path, exist_ok=True)

	with mp.Pool(n_cores) as pool:

		city_obj = City(city, sim_general_conf)
		sim_conf_grid = EFFCS_SimConfGrid(sim_scenario_conf_grid)

		pool_stats_list = []
		for i in np.arange(0, len(sim_conf_grid.conf_list), n_cores):

			conf_tuples = []

			for sim_scenario_conf in sim_conf_grid.conf_list[i: i + n_cores]:
				conf_tuples += [(
					sim_general_conf,
					sim_scenario_conf,
					city_obj
				)]
				conf_tuples += [(
					sim_general_conf,
					sim_scenario_conf,
					city_obj,
					sim_run_mode,
					sim_scenario_name,
				)]

			if sim_type == "eventG":

				sim_inputs = pool.map\
					(get_eventG_input, conf_tuples)

				pool_stats_list += pool.map\
					(get_eventG_sim_stats, sim_inputs)

			elif sim_type == "traceB":

				sim_inputs = pool.map \
					(get_traceB_input, conf_tuples)

				pool_stats_list += pool.map \
					(get_traceB_sim_stats, sim_inputs)

			print ("Batch", i / n_cores, datetime.datetime.now())

	sim_stats_df = pd.concat([sim_stats for sim_stats in pool_stats_list], axis=1, ignore_index=True).T

	sim_stats_df.to_csv(os.path.join(results_path, "sim_stats.csv"))
	pd.Series(sim_general_conf).to_csv(os.path.join(results_path, "sim_general_conf.csv"))
	pd.Series(sim_scenario_conf_grid).to_csv(os.path.join(results_path, "sim_scenario_conf_grid.csv"))

	sim_stats_df.to_pickle(os.path.join(results_path, "sim_stats.pickle"))
	pd.Series(sim_general_conf).to_pickle(os.path.join(results_path, "sim_general_conf.pickle"))
	pd.Series(sim_scenario_conf_grid).to_pickle(os.path.join(results_path, "sim_scenario_conf_grid.pickle"))

	plotter = EFFCS_MultipleRunsPlotter(
		city, sim_scenario_name, sim_general_conf, sim_scenario_conf_grid,
		"alpha", "fraction_unsatisfied", "beta"
	)
	plotter.plot_x_y_param()

	plotter = EFFCS_MultipleRunsPlotter(
		city, sim_scenario_name, sim_general_conf, sim_scenario_conf_grid,
		"alpha", "fraction_not_same_zone_trips", "beta"
	)
	plotter.plot_x_y_param()

	plotter = EFFCS_MultipleRunsPlotter(
		city, sim_scenario_name, sim_general_conf, sim_scenario_conf_grid,
		"alpha", "fraction_no_close_cars", "beta"
	)
	plotter.plot_x_y_param()

	plotter = EFFCS_MultipleRunsPlotter(
		city, sim_scenario_name, sim_general_conf, sim_scenario_conf_grid,
		"alpha", "fraction_not_enough_energy", "beta"
	)
	plotter.plot_x_y_param()
