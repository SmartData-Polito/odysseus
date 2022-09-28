import os
import pytz
import pandas as pd

from odysseus.utils.path_utils import check_create_path
from odysseus.utils.time_utils import get_time_group_columns
from odysseus.path_config.path_config import data_paths_dict
from odysseus.city_data_manager.od_matrices.od_data_source import ODmatrixDataSource


class virtualODDataSource(ODmatrixDataSource):

    def __init__(self, city_name, data_source_id, vehicles_type_id):

        super().__init__(city_name, data_source_id, vehicles_type_id)

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
        It stores normalized data both in a csv file and in a pickle file. The files produced are of the format
        *<year>_<month number>.csv* (or .pickle). For example *2017_11.csv*.

        :return: nothing
        """

    def load_norm(self, year, month):
        """
        Load a previously created normalized file from memory. It requests month and year as parameters, and checks if
        the file for that period exists in memory (looking for it with the same format as *save_norm* in the city folder).
        If it exists, it returns a pandas.DataFrame containing the data read, otherwise it returns an empty DataFrame

        :param year: year expressed as a four-digit number (e.g. 1999)
        :type year: int
        :param month: month expressed as a number (e.g. for November the method expects to receive 11)
        :type month: int
        :return: If the file exists, it returns a pandas.DataFrame containing the data read, otherwise it returns an empty DataFrame
        """
        data_path = os.path.join(
            data_paths_dict[self.city_name]["norm"][self.data_type_id],
            self.data_source_id,
            "_".join([str(year), str(month)]) + ".csv"
        )
