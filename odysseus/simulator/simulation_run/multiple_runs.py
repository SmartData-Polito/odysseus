import os
import datetime
import multiprocessing as mp
import sys
import traceback

import pandas as pd
from tqdm import tqdm

from odysseus.simulator.simulation_input.sim_config_grid import SimConfGrid
from odysseus.simulator.simulation_run.sim_run import *
from odysseus.utils.path_utils import get_output_path


def multiple_runs(config_grids_dict, configs_list, n_cpus=mp.cpu_count()):

	sim_general_config_grid = config_grids_dict["sim_general_config_grid"]
	demand_model_config_grid = config_grids_dict["demand_model_config_grid"]
	supply_model_config_grid = config_grids_dict["supply_model_config_grid"]

	# Cannot have multiple cities or scenario names in a multiple run configuration
	sim_scenario_name = config_grids_dict["sim_general_config_grid"]["sim_scenario_name"][0]
	city = config_grids_dict["sim_general_config_grid"]["city"][0]

	results_path = get_output_path("results", city, sim_scenario_name, "multiple_runs")

	pool = mp.Pool(n_cpus, maxtasksperchild=1)

	with tqdm(
			total=len(configs_list), unit="sim", postfix=str(n_cpus)+" cpu(s)", smoothing=0, dynamic_ncols=True
	) as pbar:

		def print_error(err):
			tqdm.write(
				str(datetime.datetime.now()) + " ERROR: Simulation failed! Cause: " + str(err) + " " + \
				traceback.format_exc(),
				file=sys.stderr
			)
			pbar.update()

		async_results = list()
		results_list = list()

		def collect_result(res):
			results_list.append(res)
			pbar.update()

		for conf_tuple in configs_list:
			# print(conf_tuple)
			async_result = pool.apply_async(
				run_sim_only_stats,
				(conf_tuple,),
				callback=collect_result,
				error_callback=print_error
			)
			async_results.append(async_result)

		[result.wait() for result in async_results]

	pool.close()

	print(datetime.datetime.now(), city, "multiple runs finished!")

	sim_stats_df = pd.concat([
		pd.Series(res) for res in results_list
	], axis=1, ignore_index=True).T

	sim_stats_df.to_csv(os.path.join(results_path, "sim_stats.csv"))
	pd.Series(sim_general_config_grid).to_csv(os.path.join(results_path, "sim_general_config_grid.csv"), header=True)
	pd.Series(demand_model_config_grid).to_csv(os.path.join(results_path, "demand_model_config_grid.csv"), header=True)
	pd.Series(supply_model_config_grid).to_csv(os.path.join(results_path, "sim_scenario_config_grid.csv"), header=True)

	sim_stats_df.to_pickle(os.path.join(results_path, "sim_stats.pickle"))
	pd.Series(sim_general_config_grid).to_pickle(os.path.join(results_path, "sim_general_config_grid.pickle"))
	pd.Series(demand_model_config_grid).to_csv(os.path.join(results_path, "demand_model_config_grid.pickle"))
	pd.Series(supply_model_config_grid).to_pickle(os.path.join(results_path, "sim_scenario_config_grid.pickle"))
