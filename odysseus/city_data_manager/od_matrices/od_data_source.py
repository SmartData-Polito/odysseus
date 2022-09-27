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

    :param data_source_id: Data source from which the information is taken. This allows us to have multiple data sources associated with the same city (for example from different operators)
    :type data_source_id: str

    :param vehicles_type_id: Type of service represented by the data source (e.g. car sharing or e-scooter)
    :type vehicles_type_id: str

    """

    def __init__(self, city_name, data_source_id, vehicles_type_id):

        self.city_name = city_name
        self.data_source_id = data_source_id
        self.vehicles_type_id = vehicles_type_id
        self.data_type_id = "od_matrices"

        self.raw_data_path = os.path.join(
            data_paths_dict[self.city_name]["raw"][self.data_type_id],
            self.data_source_id,
        )

        self.norm_data_path = os.path.join(
            data_paths_dict[self.city_name]["norm"][self.data_type_id],
            self.data_source_id
        )
        check_create_path(self.norm_data_path)

        self.trips_df = pd.DataFrame()
        self.trips_df_norm = pd.DataFrame()

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
        self.trips_df_norm = get_time_group_columns(self.trips_df_norm)
        return self.trips_df_norm

    def save_norm(self):
        """
        It stores normalized data both in a csv file and in a pickle file. The files produced are of the format
        *<year>_<month number>.csv* (or .pickle). For example *2017_11.csv*.

        :return: nothing
        """
        print(self.trips_df_norm.shape)

        for year in self.trips_df_norm.start_year.unique():
            for month in self.trips_df_norm.start_month.unique():

                trips_df_norm_year_month = self.trips_df_norm[
                    (self.trips_df_norm.start_year == year) & (self.trips_df_norm.start_month == month)
                    ]

                print(trips_df_norm_year_month.shape)

                if len(trips_df_norm_year_month):
                    trips_df_norm_year_month.to_csv(
                        os.path.join(
                            self.norm_data_path,
                            "_".join([str(year), str(month)]) + ".csv"
                        )
                    )
                    trips_df_norm_year_month.to_pickle(
                        os.path.join(
                            self.norm_data_path,
                            "_".join([str(year), str(month)]) + ".pickle"
                        )
                    )

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
        if os.path.exists(data_path):
            self.trips_df_norm = pd.read_csv(data_path).iloc[:, 1:]
            return self.trips_df_norm
        else:
            return pd.DataFrame()
