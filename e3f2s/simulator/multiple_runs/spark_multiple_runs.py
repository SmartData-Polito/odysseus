from e3f2s.simulator.data_structures.city import City
from e3f2s.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid
from e3f2s.simulator.single_run.run_eventG_sim import get_eventG_sim_stats

from pyspark import SparkConf, SparkContext


broadcastVar = ""


def spark_multiple_runs(sim_run_conf, sim_general_conf, sim_scenario_conf_grid):

    conf = (SparkConf().setAppName("Spark trial for e3f2s"))
    sc = SparkContext(conf=conf)

    city = sim_run_conf["city"]
    city_obj = City(city, sim_run_conf["data_source_id"], sim_general_conf)

    global broadcastVar
    broadcastVar = sc.broadcast(city_obj)

    sim_conf_grid = EFFCS_SimConfGrid(sim_scenario_conf_grid)

    conf_tuples = []

    for sim_scenario_conf in sim_conf_grid.conf_list:
        conf_tuples += [(
            sim_general_conf,
            sim_scenario_conf,
            city_obj
        )]

    bs_rdd = sc.parallelize(conf_tuples, numSlices=len(conf_tuples))
    sim_stats_list = bs_rdd.map(get_eventG_sim_stats).collectAsMap()
    print(sim_stats_list)
