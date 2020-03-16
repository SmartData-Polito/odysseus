import itertools
import datetime
import numpy as np
import pandas as pd


class EFFCS_SimConfGrid ():
    
    def __init__ (self, general_conf, conf_grid):

        self.conf_keys = conf_grid.values()
        self.conf_list = []        
        for el in itertools.product(*conf_grid.values()):
            conf = {k:None for k in conf_grid}
            i = 0
            for k in conf.keys():
                conf[k] = el[i]
                i += 1
            self.conf_list += [conf]
        self.conf_list = pd.DataFrame(self.conf_list).drop_duplicates().to_dict("records")
