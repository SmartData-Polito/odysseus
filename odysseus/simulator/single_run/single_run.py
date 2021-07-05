import datetime
import os
import pickle

import pandas as pd

from odysseus.simulator.single_run.get_traceB_input import get_traceB_input
from odysseus.simulator.single_run.get_eventG_input import get_eventG_input
from odysseus.simulator.single_run.run_traceB_sim import run_traceB_sim
from odysseus.simulator.single_run.run_eventG_sim import run_eventG_sim
from odysseus.simulator.simulation_output.sim_output import SimOutput
from odysseus.simulator.simulation_output.sim_output_plotter import EFFCS_SimOutputPlotter


def single_run(conf_dict):

    sim_general_conf = conf_dict["sim_general_conf"]
    sim_scenario_conf = conf_dict["sim_scenario_conf"]
    sim_scenario_name = conf_dict["sim_scenario_name"]
    supply_model_object = conf_dict["supply_model_object"]
    demand_model_folder = conf_dict["demand_model_folder"]

    city = sim_general_conf["city"]
    sim_type = sim_general_conf["sim_technique"]

    results_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "results",
        city,
        "single_run",
        sim_scenario_name,
        str(sim_scenario_conf["conf_id"])
    )
    os.makedirs(results_path, exist_ok=True)

    figures_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "figures",
        city,
        "single_run",
        sim_scenario_name,
        str(sim_scenario_conf["conf_id"])
    )
    os.makedirs(figures_path, exist_ok=True)

    print(city, datetime.datetime.now(), "City initialised!")

    input_parameters = {
        "sim_general_conf": sim_general_conf,
        "sim_scenario_conf": sim_scenario_conf,
        "supply_model_object": supply_model_object,
        "demand_model_folder": demand_model_folder
    }

    if sim_type == "eventG":
        simInput_eventG = get_eventG_input(input_parameters)
        sim_eventG = run_eventG_sim(sim_input=simInput_eventG)
        simOutput_eventG = SimOutput(sim_eventG, results_path, sim_general_conf, sim_scenario_conf)
        sim_stats = simOutput_eventG.sim_stats
        simOutput = simOutput_eventG
    elif sim_type == "traceB":
        simInput_traceB = get_traceB_input(input_parameters)
        sim_traceB = run_traceB_sim (sim_input=simInput_traceB)
        simOutput_traceB = SimOutput(sim_traceB, results_path, sim_general_conf, sim_scenario_conf)
        sim_stats = simOutput_traceB.sim_stats
        simOutput = simOutput_traceB

    print(datetime.datetime.now(), city, sim_scenario_name, sim_scenario_conf["conf_id"], "finished!")

    sim_stats.to_pickle(os.path.join(results_path, "sim_stats.pickle"))
    sim_stats.to_csv(os.path.join(results_path, "sim_stats.csv"))
    pd.Series(sim_general_conf).to_pickle(os.path.join(results_path, "sim_general_conf.pickle"))
    pd.Series(sim_scenario_conf).to_pickle(os.path.join(results_path, "sim_scenario_conf.pickle"))

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

    return sim_stats
