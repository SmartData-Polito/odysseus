import json
import pickle
import datetime

from odysseus.city_scenario.city_data_loader import CityDataLoader
from odysseus.utils.time_utils import *
from odysseus.utils.geospatial_utils import *
from odysseus.path_config.path_config import *

from odysseus.city_scenario.energymix_loader import EnergyMix
from odysseus.city_scenario.abstract_city_scenario import AbstractCityScenario


class CityScenario(AbstractCityScenario):

    def __init__(self, city_name, read_config_from_file=False, city_scenario_config=None, in_folder_name=None):

        super(CityScenario, self).__init__(city_name)
        self.bin_side_length = city_scenario_config["bin_side_length"]

        if read_config_from_file and in_folder_name:
            self.folder_name = in_folder_name
        elif city_scenario_config:
            self.city_scenario_config = city_scenario_config
            self.folder_name = self.city_scenario_config["folder_name"]
        else:
            raise IOError("Wrong arguments for CityScenario!")

        self.city_scenario_path = os.path.join(
            city_scenarios_path,
            city_name,
            self.folder_name
        )
        if read_config_from_file and in_folder_name:
            self.read_config_from_folder_name()
