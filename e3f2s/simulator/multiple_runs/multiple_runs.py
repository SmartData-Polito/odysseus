import os
import pickle
import datetime
import multiprocessing as mp

import pandas as pd

from e3f2s.demand_modelling.city import City
from e3f2s.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid
from e3f2s.simulator.single_run.run_eventG_sim import get_eventG_sim_stats
from e3f2s.simulator.single_run.run_traceB_sim import get_traceB_sim_stats


def multiple_runs(sim_general_conf, sim_scenario_conf_grid, sim_scenario_name):

	sim_technique = sim_general_conf["sim_technique"]
	city = sim_general_conf["city"]

	results_path = os.path.join(
		os.path.dirname(os.path.dirname(__file__)),
		"results",
		city,
		"multiple_runs",
		sim_scenario_name,
	)
	os.makedirs(results_path, exist_ok=True)

	demand_model_path = os.path.join(
		os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
		"demand_modelling",
		"demand_models",
		sim_general_conf["city"],
	)

	with mp.Pool(mp.cpu_count()) as pool:

		city_obj = pickle.Unpickler(open(os.path.join(demand_model_path, "city_obj.pickle"), "rb")).load()

		sim_conf_grid = EFFCS_SimConfGrid(sim_scenario_conf_grid)

		pool_stats_list = []
		conf_tuples = []

		for sim_scenario_conf in sim_conf_grid.conf_list:
			if "const_load_factor" in sim_general_conf.keys():
				if sim_general_conf["const_load_factor"] != False:
					round_lambda = round(sim_scenario_conf["requests_rate_factor"], 2)
					round_vehicles_factor = round(sim_scenario_conf["n_vehicles_factor"], 2)
					if round(round_lambda / round_vehicles_factor, 2) == sim_general_conf["const_load_factor"]:
						conf_tuples += [(
							sim_general_conf,
							sim_scenario_conf,
							city_obj
						)]
				else:
					conf_tuples += [(
						sim_general_conf,
						sim_scenario_conf,
						city_obj
					)]
			else:
				conf_tuples += [(
					sim_general_conf,
					sim_scenario_conf,
					city_obj
				)]

		if sim_technique == "eventG":
			pool_stats_list += pool.map(get_eventG_sim_stats, conf_tuples)
		elif sim_technique == "traceB":
			pool_stats_list += pool.map(get_traceB_sim_stats, conf_tuples)

	print(datetime.datetime.now(), city, "multiple runs finished!")

	sim_stats_df = pd.concat([sim_stats for sim_stats in pool_stats_list], axis=1, ignore_index=True).T
	sim_stats_df.to_csv(os.path.join(results_path, "sim_stats.csv"))
	pd.Series(sim_general_conf).to_csv(os.path.join(results_path, "sim_general_conf.csv"), header=True)
	pd.Series(sim_scenario_conf_grid).to_csv(os.path.join(results_path, "sim_scenario_conf_grid.csv"), header=True)

	sim_stats_df.to_pickle(os.path.join(results_path, "sim_stats.pickle"))
	pd.Series(sim_general_conf).to_pickle(os.path.join(results_path, "sim_general_conf.pickle"))
	pd.Series(sim_scenario_conf_grid).to_pickle(os.path.join(results_path, "sim_scenario_conf_grid.pickle"))
