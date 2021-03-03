import os
import itertools

import pandas as pd
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')
matplotlib.rcParams["axes.grid"] = True

import seaborn as sns


class EFFCS_MultipleRunsPlotter:

    def __init__(
            self,
            city,
            sim_scenario_name,
            sim_general_conf,
            sim_scenario_conf_grid,
            x_col,
            y_col,
            param_col
    ):

        self.city = city
        self.x_col = x_col
        self.y_col = y_col
        self.param_col = param_col

        model_general_conf_string = "_".join([str(v) for v in sim_general_conf.values()]).replace("'", "").replace(".", "d")
        model_scenario_conf_grid_string = "_".join([
            str(v) for v in sim_scenario_conf_grid.values()
        ]).replace(" ", "-").replace("'", "").replace(".", "d").replace(",", "-").replace("[", "-").replace("]", "-")

        self.results_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "results",
            city,
            "multiple_runs",
            sim_scenario_name,
            model_general_conf_string,
            model_scenario_conf_grid_string
        )
        self.figures_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "figures",
            city,
            "multiple_runs",
            sim_scenario_name,
            model_general_conf_string,
            model_scenario_conf_grid_string
        )
        os.makedirs(self.figures_path, exist_ok=True)

        self.sim_stats_df = pd.read_pickle(os.path.join(self.results_path, "sim_stats.pickle"))

        self.sim_stats_df.n_cars_factor = \
            self.sim_stats_df.n_cars_factor.apply(lambda x: np.around(x, decimals=2))

    def plot_x_y_param(self):
        fig, ax = plt.subplots(figsize=(15, 7))
        plt.xlabel(self.x_col)
        plt.ylabel(self.y_col)
        marker = itertools.cycle(('.', 'v', '^', '>', '<', '1', '2'))
        for group in self.sim_stats_df[self.param_col].unique():
            group_plot_df = self.sim_stats_df.loc[self.sim_stats_df[self.param_col] == group]
            group_plot_df.set_index(self.x_col)[self.y_col].plot(
                ax=ax, marker=next(marker), legend=True,
                label="=".join([self.param_col, str(group)])
            )
        plt.legend()
        plt.savefig(
            os.path.join(
                self.figures_path,
                "_".join([self.y_col, self.x_col]) + ".pdf"
            )
        )


