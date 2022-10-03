import os
import pytz
import pandas as pd

from odysseus.utils.path_utils import check_create_path
from odysseus.utils.time_utils import get_time_group_columns
from odysseus.path_config.path_config import data_paths_dict


class ODmatrixDataSource:

    """

    ODmatrixDataSource is a class that contains procedures to read and process OD matrices.

    :param city_name: City name.
    :type city_name: str

    :param data_source_id: Data source from which the information is taken.
    This allows us to have multiple data sources associated with the same city (for example from different operators)
    :type data_source_id: str

    :param vehicles_type_id: Type of service represented by the data source (e.g. car sharing or e-scooter)
    :type vehicles_type_id: str

    """

    def __init__(self, city_name, data_source_id):

        self.city_name = city_name
        self.data_source_id = data_source_id
        self.data_type_id = "od_matrices"

    def load_raw(self):

        """
        Method for loading raw od matrices. Since the data format might differs in the various datasets, the method
        is left abstract. Each city has its own implementation.

        :return: nothing
        """

        return

    def normalise(self):
        """
        This method is used to standardize the data format. Again the implementation is highly dependent on the data
        source and almost all modules override the method.

        :return: A normalized pandas.DataFrame
        """

    def save_norm(self):
        """
        It stores normalized data as a collection of .csv containing OD matrices for a certain week_slot and day_slot.
        It also stores the .json configurations for the city grid and the time division.

        :return: nothing
        """

    def load_norm(self, year, month):
        """
        Load a previously created set of OD matrices with their configurations.
        """

