import os
import pandas as pd

from e3f2s.simulator.data_structures.city import City
from e3f2s.simulator.simulation_input.sim_config_grid import EFFCS_SimConfGrid
from e3f2s.simulator.simulation_input.sim_input import SimInput
from pyspark import SparkConf, SparkContext

broadcastVar = ""


