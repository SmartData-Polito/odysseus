import os
import pandas as pd

from city_data_manager.config.config import root_data_path

class Loader ():
    
    def __init__ (self, city, year, month):
        
        self.city = city
        self.year = year
        self.month = month
        self.norm_data_path = os.path.join(
            root_data_path,
            self.city,
            "2019_5",
            "city_of_minneapolis"
        )

    def read_bookings_grid (self):

        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "Data",
            self.city,
            "bookings.pickle"
        )
        self.bookings = pd.read_pickle(path)
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "Data",
            self.city,
            "grid.pickle"
        )
        self.grid = pd.read_pickle(path)

        return self.bookings, self.grid
