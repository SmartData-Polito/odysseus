import os
import pickle

import pandas as pd

from simulator.data_structures.city import City
from simulator.single_run.get_traceB_input import get_traceB_input
from simulator.single_run.get_eventG_input import get_eventG_input
from simulator.single_run.run_traceB_sim import run_traceB_sim
from simulator.single_run.run_eventG_sim import run_eventG_sim
from simulator.simulation_output.sim_output import EFFCS_SimOutput
from simulator.simulation_output.sim_output_plotter import EFFCS_SimOutputPlotter


def single_run(conf_tuple):

	city = conf_tuple[0]["city"]
	data_source_id = conf_tuple[0]["data_source_id"]
	sim_general_conf = conf_tuple[1]
	sim_scenario_conf = conf_tuple[2]
	sim_scenario_name = conf_tuple[3]
	sim_type = conf_tuple[0]["sim_technique"]

	city_obj = City(city, data_source_id, sim_general_conf)

	model_general_conf_string = "_".join([
		str(v) for v in sim_general_conf.values()]
	).replace("'", "").replace(".", "d")
	model_conf_string = "_".join([
		str(v) for v in sim_scenario_conf.values()]
	).replace("'", "").replace(".", "d")
	results_path = os.path.join(
		os.path.dirname(os.path.dirname(__file__)),
		"results",
		city,
		"single_run",
		sim_scenario_name,
		model_general_conf_string,
		model_conf_string
	)
	os.makedirs(results_path, exist_ok=True)

	if sim_type == "eventG":

		simInput_eventG = get_eventG_input((sim_general_conf, sim_scenario_conf, city_obj))
		sim_eventG = run_eventG_sim(simInput=simInput_eventG)
		simOutput_eventG = EFFCS_SimOutput(sim_eventG)
		sim_stats = simOutput_eventG.sim_stats
		simOutput = simOutput_eventG

	elif sim_type == "traceB":

		simInput_traceB = get_traceB_input((sim_general_conf, sim_scenario_conf, city_obj))
		sim_traceB = run_traceB_sim (simInput=simInput_traceB)
		simOutput_traceB = EFFCS_SimOutput(sim_traceB)
		sim_stats = simOutput_traceB.sim_stats
		simOutput = simOutput_traceB

	sim_stats.to_pickle(os.path.join(results_path, "sim_stats.pickle"))
	pd.Series(sim_general_conf).to_pickle(os.path.join(results_path, "sim_general_conf.pickle"))
	pd.Series(sim_scenario_conf).to_pickle(os.path.join(results_path, "sim_scenario_conf.pickle"))

	simOutput.grid.to_pickle(
		os.path.join(
			results_path,
			"grid.pickle"
		)
	)

	simOutput.sim_booking_requests.to_pickle(
		os.path.join(
			results_path,
			"sim_booking_requests.pickle"
		)
	)
	simOutput.sim_bookings.to_pickle(
		os.path.join(
			results_path,
			"sim_bookings.pickle"
		)
	)
	simOutput.sim_charges.to_pickle(
		os.path.join(
			results_path,
			"sim_charges.pickle"
		)
	)
	simOutput.sim_not_enough_energy_requests.to_pickle(
		os.path.join(
			results_path,
			"sim_unsatisfied_no-energy.pickle"
		)
	)
	simOutput.sim_no_close_vehicle_requests.to_pickle(
		os.path.join(
			results_path,
			"sim_unsatisfied_no_close_vehicle.pickle"
		)
	)
	simOutput.sim_unsatisfied_requests.to_pickle(
		os.path.join(
			results_path,
			"sim_unsatisfied_requests.pickle"
		)
	)
	simOutput.sim_system_charges_bookings.to_pickle(
		os.path.join(
			results_path,
			"sim_system_charges_bookings.pickle"
		)
	)
	simOutput.sim_users_charges_bookings.to_pickle(
		os.path.join(
			results_path,
			"sim_users_charges_bookings.pickle"
		)
	)
	simOutput.sim_unfeasible_charge_bookings.to_pickle(
		os.path.join(
			results_path,
			"sim_unfeasible_charge_bookings.pickle"
		)
	)
	simOutput.sim_charge_deaths.to_pickle(
		os.path.join(
			results_path,
			"sim_unfeasible_charges.pickle"
		)
	)

	simOutput.n_vehicles_per_zones_history.to_pickle(
		os.path.join(
			results_path,
			"n_vehicles_per_zones_history.pickle"
		)
	)
	simOutput.n_vehicles_per_zones_history.to_csv(
		os.path.join(
			results_path,
			"n_vehicles_per_zones_history.csv"
		)
	)

	simOutput.vehicles_history.to_csv(
		os.path.join(
			results_path,
			"vehicles_history.csv"
		)
	)

	plotter = EFFCS_SimOutputPlotter(simOutput, city, sim_scenario_name)
	plotter.plot_events_profile_barh()
	plotter.plot_events_t()
	plotter.plot_fleet_status_t()
	plotter.plot_events_hourly_count_boxplot("bookings", "start")
	plotter.plot_events_hourly_count_boxplot("charges", "start")
	plotter.plot_events_hourly_count_boxplot("unsatisfied", "start")
	plotter.plot_n_vehicles_charging_hourly_mean_boxplot()

	for col in [
		"origin_count",
		#"destination_count",
		#"charge_needed_system_zones_count",
		#"charge_needed_users_zones_count",
		"unsatisfied_demand_origins_fraction",
		#"not_enough_energy_origins_count",
		#"charge_deaths_origins_count",
	]:
		if col in simOutput.grid:
			plotter.plot_choropleth(col)

	return sim_stats
