import os
import pickle
import datetime
import multiprocessing as mp

import pandas as pd

from e3f2s.simulator.simulation_data_structures.city import City
from e3f2s.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid
from e3f2s.simulator.single_run.get_traceB_input import get_traceB_input
from e3f2s.simulator.single_run.get_eventG_input import get_eventG_input
from e3f2s.simulator.single_run.run_eventG_sim import get_eventG_sim_stats
from e3f2s.simulator.single_run.run_traceB_sim import get_traceB_sim_stats


def multiple_runs(sim_general_conf, sim_scenario_conf_grid, sim_scenario_name):

	sim_technique = sim_general_conf["sim_technique"]

	for city in sim_general_conf["city"]:

		# model_general_conf_string = "_".join([str(v) for v in sim_general_conf.values()]).replace("'", "").replace(".", "d")
		# model_scenario_conf_grid_string = "_".join([
		# 	str(v) for v in sim_scenario_conf_grid.values()
		# ]).replace(" ", "-").replace("'", "").replace(".", "d").replace(",", "-").replace("[", "-").replace("]", "-")

		results_path = os.path.join(
			os.path.dirname(os.path.dirname(__file__)),
			"results",
			city,
			"multiple_runs",
			sim_scenario_name,
		)
		os.makedirs(results_path, exist_ok=True)

		with mp.Pool(mp.cpu_count()) as pool:

			if not os.path.exists(os.path.join(results_path, "city_obj.pickle")):
				city_obj = City(city, sim_general_conf["data_source_id"], sim_general_conf)
				pickle.dump(
					city_obj,
					open(os.path.join(results_path, "city_obj.pickle"), "wb")
				)
				city_obj.grid_matrix.to_pickle(
					os.path.join(results_path, "grid_matrix.pickle")
				)
				pd.DataFrame(city_obj.neighbors_dict).to_pickle(
					os.path.join(results_path, "neighbors_dict.pickle")
				)
			else:
				city_obj = pickle.Unpickler(open(os.path.join(results_path, "city_obj.pickle"), "rb")).load()

			sim_conf_grid = EFFCS_SimConfGrid(sim_scenario_conf_grid)

			pool_stats_list = []
			conf_tuples = []

			if "const_load_factor" in sim_general_conf.keys():
				if sim_general_conf["const_load_factor"] != False:
					for sim_scenario_conf in sim_conf_grid.conf_list:
						round_lambda = round(sim_scenario_conf["requests_rate_factor"], 2)
						round_vehicles_factor = round(sim_scenario_conf["n_vehicles_factor"], 2)
						if round(round_lambda / round_vehicles_factor, 2) == sim_general_conf["const_load_factor"]:
							conf_tuples += [(
								sim_general_conf,
								sim_scenario_conf,
								city_obj
							)]
				else:
					for sim_scenario_conf in sim_conf_grid.conf_list:
						conf_tuples += [(
							sim_general_conf,
							sim_scenario_conf,
							city_obj
						)]
			else:
				for sim_scenario_conf in sim_conf_grid.conf_list:
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
