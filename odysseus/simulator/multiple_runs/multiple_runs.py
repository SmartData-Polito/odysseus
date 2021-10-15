import os
import datetime
import multiprocessing as mp
import sys
import traceback

import pandas as pd
from tqdm import tqdm

from odysseus.simulator.simulation_input.sim_config_grid import SimConfGrid
from odysseus.simulator.single_run.run_eventG_sim import get_eventG_sim_stats
from odysseus.simulator.single_run.run_traceB_sim import get_traceB_sim_stats
from odysseus.utils.path_utils import get_output_path


def multiple_runs(conf_dict):
	sim_general_conf = conf_dict["sim_general_conf"]
	sim_scenario_conf_grid = conf_dict["sim_scenario_conf"]
	sim_scenario_name = conf_dict["sim_scenario_name"]
	supply_model_object = conf_dict["supply_model_object"]
	demand_model_folder = conf_dict["demand_model_folder"]

	if "n_cpus" not in conf_dict:
		n_cpus = mp.cpu_count()
	else:
		n_cpus = conf_dict["n_cpus"]

	sim_technique = sim_general_conf["sim_technique"]
	city = sim_general_conf["city"]
	results_path = get_output_path("results", sim_general_conf["city"], sim_scenario_name, "multiple_runs")

	with mp.Pool(n_cpus, maxtasksperchild=1) as pool:

		sim_conf_grid = SimConfGrid(sim_scenario_conf_grid)

		pool_stats_dict = {}
		conf_tuples = []

		for conf_id, sim_scenario_conf in enumerate(sim_conf_grid.conf_list):
			sim_scenario_conf["conf_id"] = conf_id
			if "const_load_factor" in sim_general_conf.keys():
				if sim_general_conf["const_load_factor"] != False:
					round_lambda = round(sim_scenario_conf["requests_rate_factor"], 2)
					round_vehicles_factor = round(sim_scenario_conf["n_vehicles_factor"], 2)
					if round(round_lambda / round_vehicles_factor, 2) == sim_general_conf["const_load_factor"]:
						conf_tuples += [(
							sim_general_conf,
							sim_scenario_conf,
							demand_model_folder,
							supply_model_object
						)]
				else:
					conf_tuples += [(
						sim_general_conf,
						sim_scenario_conf,
						demand_model_folder,
						supply_model_object
					)]
			else:
				conf_tuples += [(
					sim_general_conf,
					sim_scenario_conf,
					demand_model_folder,
					supply_model_object
				)]

		with tqdm(
				total=len(conf_tuples), unit="sim", postfix=str(n_cpus)+" cpu(s)", smoothing=0, dynamic_ncols=True
		) as pbar:

			def collect_result(res):
				res_id = res["conf_id"]
				pool_stats_dict[res_id] = res
				pbar.update()

			def print_error(err):
				tqdm.write(
					str(datetime.datetime.now()) + " ERROR: Simulation failed! Cause: " + str(err) + " " + \
					traceback.format_exc(),
					file=sys.stderr
				)
				pbar.update()

			async_results = []

			if sim_technique == "eventG":
				for conf_tuple in conf_tuples:
					async_result = pool.apply_async(
						get_eventG_sim_stats, (conf_tuple,), callback=collect_result, error_callback=print_error
					)
					async_results.append(async_result)
			elif sim_technique == "traceB":
				for conf_tuple in conf_tuples:
					async_result = pool.apply_async(
						get_traceB_sim_stats, (conf_tuple,), callback=collect_result, error_callback=print_error
					)
					async_results.append(async_result)

			[result.wait() for result in async_results]

	print(datetime.datetime.now(), city, "multiple runs finished!")

	sim_stats_df = pd.concat([pool_stats_dict[res_id] for res_id in sorted(pool_stats_dict)], axis=1, ignore_index=True).T
	sim_stats_df.to_csv(os.path.join(results_path, "sim_stats.csv"))
	pd.Series(sim_general_conf).to_csv(os.path.join(results_path, "sim_general_conf.csv"), header=True)
	pd.Series(sim_scenario_conf_grid).to_csv(os.path.join(results_path, "sim_scenario_conf_grid.csv"), header=True)

	sim_stats_df.to_pickle(os.path.join(results_path, "sim_stats.pickle"))
	pd.Series(sim_general_conf).to_pickle(os.path.join(results_path, "sim_general_conf.pickle"))
	pd.Series(sim_scenario_conf_grid).to_pickle(os.path.join(results_path, "sim_scenario_conf_grid.pickle"))
