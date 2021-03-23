import os
import datetime
import pandas as pd

from odysseus.simulator.simulation_input.sim_current_config.sim_general_conf import sim_general_conf_grid
from odysseus.simulator.simulation_input.sim_current_config.multiple_runs_conf import sim_scenario_conf_grid

from odysseus.scenario_generator.city import City
from odysseus.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid
from odysseus.simulator.simulation_input.sim_input import SimInput
from odysseus.simulator.simulation.model_driven_simulator import ModelDrivenSim
from odysseus.simulator.simulation_output.sim_output import SimOutput

from pyspark import SparkConf, SparkContext

conf = (SparkConf().setAppName("Spark trial for odysseus"))
sc = SparkContext(conf=conf)
broadcastVar = ""


def run_eventG_sim(simInput):
    sim_eventG = ModelDrivenSim(

        simInput=simInput

    )
    sim_eventG.init_data_structures()
    sim_eventG.run()
    return sim_eventG


def get_eventG_sim_output(simInput):
    sim_eventG = run_eventG_sim(simInput)
    return SimOutput(sim_eventG)


def get_eventG_sim_stats_spark (conf_tuple):

    conf_tuple = (conf_tuple[0], conf_tuple[1], broadcastVar.value)
    simInput = SimInput(conf_tuple)
    simInput.get_booking_requests_list()
    simInput.init_vehicles()
    simInput.init_hub()
    simInput.init_charging_poles()
    sim_eventG = run_eventG_sim(simInput)
    simOutput_eventG = SimOutput(sim_eventG)
    return simOutput_eventG.sim_stats


def spark_multiple_runs(sim_general_conf, sim_scenario_conf_grid, sim_scenario_name):

    city = sim_general_conf["city"]

    print(city, sim_scenario_name)

    results_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "results",
        city,
        "multiple_runs",
        sim_scenario_name,
    )
    os.makedirs(results_path, exist_ok=True)

    print("Here 1!")

    city_obj = City(city, sim_general_conf["data_source_id"], sim_general_conf)

    global broadcastVar
    broadcastVar = sc.broadcast(city_obj)

    print("Here 2!")

    sim_conf_grid = EFFCS_SimConfGrid(sim_scenario_conf_grid)

    conf_tuples = []

    for sim_scenario_conf in sim_conf_grid.conf_list:
        conf_tuples += [(
            sim_general_conf,
            sim_scenario_conf,
        )]

    bs_rdd = sc.parallelize(conf_tuples, numSlices=len(conf_tuples))

    print("Here 3!", len(conf_tuples))

    sim_stats_list = bs_rdd.map(get_eventG_sim_stats_spark).collect()

    sim_stats_df = pd.concat([sim_stats for sim_stats in sim_stats_list], axis=1, ignore_index=True).T
    sim_stats_df.to_csv(os.path.join(results_path, "sim_stats.csv"))

    return sim_stats_list


confs_dict = {}
confs_dict["spark"] = sim_scenario_conf_grid

sim_general_conf_list = EFFCS_SimConfGrid(sim_general_conf_grid).conf_list

for sim_general_conf in sim_general_conf_list:
    print(sim_general_conf)

    city_name = sim_general_conf["city"]
    sim_scenario_name = sim_general_conf["sim_scenario_name"]

    print(datetime.datetime.now(), city_name, sim_scenario_name, "starting..")

    spark_multiple_runs(
        sim_general_conf,
        sim_scenario_conf_grid,
        sim_scenario_name
    )

sc.stop()
