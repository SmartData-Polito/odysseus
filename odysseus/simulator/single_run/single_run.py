import datetime
import os
import pickle

import pandas as pd

from odysseus.simulator.simulation_input.sim_input import SimInput
from odysseus.simulator.single_run.run_traceB_sim import run_traceB_sim
from odysseus.simulator.single_run.run_eventG_sim import run_eventG_sim
from odysseus.simulator.simulation_output.sim_output import SimOutput
from odysseus.simulator.simulation_output.sim_output_plotter import EFFCS_SimOutputPlotter
from odysseus.utils.path_utils import get_output_path


def single_run(conf_dict):

    sim_general_conf = conf_dict["sim_general_conf"]
    supply_model_conf = conf_dict["supply_model_conf"]
    sim_scenario_name = conf_dict["sim_scenario_name"]

    city = sim_general_conf["city"]
    sim_technique = sim_general_conf["sim_technique"]

    results_path = get_output_path(
        "results", city, conf_dict["sim_scenario_name"], "single_run", sim_general_conf["conf_id"]
    )
    figures_path = get_output_path(
        "figures", city, conf_dict["sim_scenario_name"], "single_run", sim_general_conf["conf_id"]
    )

    print(datetime.datetime.now(), city, sim_scenario_name, sim_general_conf["conf_id"], "City scenario initialised!")

    sim_input = SimInput(conf_dict)
    sim_input.init_vehicles()
    sim_input.init_charging_poles()
    sim_input.init_relocation()

    if sim_technique == "eventG":
        sim_eventG = run_eventG_sim(sim_input=sim_input)
        simOutput_eventG = SimOutput(sim_eventG)
        simOutput_eventG.save_output(results_path, sim_general_conf, supply_model_conf)
        sim_stats = simOutput_eventG.sim_stats
        simOutput = simOutput_eventG
    elif sim_technique == "traceB":
        sim_traceB = run_traceB_sim (sim_input=sim_input)
        simOutput_traceB = SimOutput(sim_traceB)
        simOutput_traceB.save_output(results_path, sim_general_conf, supply_model_conf)
        sim_stats = simOutput_traceB.sim_stats
        simOutput = simOutput_traceB

    print(
        datetime.datetime.now(), city, sim_scenario_name, sim_general_conf["conf_id"], "Simulation finished!",
        "Creating output.."
    )

    sim_stats.to_csv(os.path.join(results_path, "sim_stats.csv"))
    pd.Series(sim_general_conf).to_csv(os.path.join(results_path, "sim_general_conf.csv"))
    pd.Series(supply_model_conf).to_csv(os.path.join(results_path, "sim_scenario_conf.csv"))

    pickle.dump(
        simOutput,
        open(os.path.join(results_path, "sim_output.pickle"), "wb")
    )

    simOutput.grid.to_pickle(
        os.path.join(
            results_path,
            "grid.pickle"
        )
    )
    simOutput.grid.to_file(
        os.path.join(
            results_path,
            "grid.dbf"
        )
    )

    if sim_general_conf["save_history"]:
        plotter = EFFCS_SimOutputPlotter(simOutput, city, sim_scenario_name, figures_path)
        plotter.plot_events_profile_barh()
        plotter.plot_events_t()
        plotter.plot_fleet_status_t()
        plotter.plot_events_hourly_count_boxplot("bookings_train", "start")
        plotter.plot_events_hourly_count_boxplot("charges", "start")
        plotter.plot_events_hourly_count_boxplot("unsatisfied", "start")
        plotter.plot_n_vehicles_charging_hourly_mean_boxplot()

        plotter.plot_city_zones()
        plotter.plot_charging_infrastructure()
        for col in [
            "origin_count",
            "destination_count",
            "charge_needed_system_zones_count",
            #"charge_needed_users_zones_count",
            "unsatisfied_demand_origins",
            "not_enough_energy_origins_count",
            "charge_deaths_origins_count",
        ]:
            if col in simOutput.grid:
                plotter.plot_choropleth(col)

    print(
        datetime.datetime.now(), city, sim_scenario_name, sim_general_conf["conf_id"],
        "Output created!"
    )

    return sim_stats
