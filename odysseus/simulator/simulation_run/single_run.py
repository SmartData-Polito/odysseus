import datetime
import os
import pickle
import json

import pandas as pd

from odysseus.simulator.simulation_run.sim_run import *
from odysseus.simulator.simulation_output.sim_output import SimOutput
from odysseus.simulator.simulation_output.sim_output_plotter import EFFCS_SimOutputPlotter
from odysseus.utils.path_utils import get_output_path


def single_run(conf_dict):

    sim_general_conf = conf_dict["sim_general_conf"]
    supply_model_conf = conf_dict["supply_model_conf"]
    sim_scenario_name = conf_dict["sim_scenario_name"]

    city = sim_general_conf["city"]

    results_path = get_output_path(
        "results", city, conf_dict["sim_scenario_name"], "single_run", conf_dict["conf_id"]
    )

    start = datetime.datetime.now()

    print(datetime.datetime.now(), city, sim_scenario_name, conf_dict["conf_id"], "Initialising SimInput..")

    sim_input = SimInput(conf_dict)
    #print(datetime.datetime.now(), city, sim_scenario_name, conf_dict["conf_id"], "Initialising vehicles..")
    sim_input.init_vehicles()
    #print(datetime.datetime.now(), city, sim_scenario_name, conf_dict["conf_id"], "Initialising charging poles..")
    sim_input.init_charging_poles()
    #print(datetime.datetime.now(), city, sim_scenario_name, conf_dict["conf_id"], "Initialising relocation..")
    sim_input.init_relocation()

    end = datetime.datetime.now()
    print(
        datetime.datetime.now(), city, sim_scenario_name, conf_dict["conf_id"],
        "SimInput initialised, duration:", (end-start).total_seconds(),
    )

    start = datetime.datetime.now()

    sim = run_sim_v2(sim_input)

    sim_output = SimOutput(sim)
    sim_stats = sim_output.sim_stats

    end = datetime.datetime.now()
    print(
        datetime.datetime.now(), city, sim_scenario_name, conf_dict["conf_id"],
        "Simulation finished, duration:", (end-start).total_seconds(), "Creating output.."
    )
    start = datetime.datetime.now()

    sim_stats.to_csv(os.path.join(results_path, "sim_stats.csv"))
    pd.Series(sim_general_conf).to_csv(os.path.join(results_path, "sim_general_conf.csv"))
    pd.Series(supply_model_conf).to_csv(os.path.join(results_path, "sim_scenario_conf.csv"))

    with open(os.path.join(results_path, "n_charging_poles_by_zone.json"), "w") as f:
        json.dump(sim_output.n_charging_poles_by_zone, f)

    sim_output.grid.to_pickle(
        os.path.join(
            results_path,
            "grid.pickle"
        )
    )

    if not sim_general_conf["exclude_sim_output_obj"]:

        pickle.dump(
            sim_output,
            open(os.path.join(results_path, "sim_output.pickle"), "wb")
        )

    if not sim_general_conf["exclude_geo_grid"]:

        sim_output.grid.to_file(
            os.path.join(
                results_path,
                "grid.dbf"
            )
        )

    sim_output.save_output(results_path, sim_general_conf, supply_model_conf)

    if sim_general_conf["auto_plotting"]:

        figures_path = get_output_path(
            "figures", city, conf_dict["sim_scenario_name"], "single_run", conf_dict["conf_id"]
        )

        plotter = EFFCS_SimOutputPlotter(sim_output, city, sim_scenario_name, figures_path)
        plotter.plot_events_profile_barh()
        if len(sim_output.sim_bookings):
            plotter.plot_events_t()
        plotter.plot_fleet_status_t()

        # TODO -> Manage auto plotting exec time because Seaborn boxplots are cool yet slow
        plotter.plot_events_hourly_count_boxplot("bookings", "start")
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
            if col in sim_output.grid:
                plotter.plot_choropleth(col)

    end = datetime.datetime.now()

    print(
        datetime.datetime.now(), city, sim_scenario_name, conf_dict["conf_id"],
        "Output created, duration: {} seconds".format((end-start).total_seconds())
    )

    return sim_stats
