import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')
matplotlib.rcParams["axes.grid"] = True
matplotlib.rcParams["figure.figsize"] = (15., 7.)

SMALL_SIZE = 8
MEDIUM_SIZE = 12
BIGGER_SIZE = 20

plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

def plot_events_percentage (sim_stats_df, 
                            x_col, 
                            title_add,
                            figpath,
                            figname):

    plt.figure(figsize=(15, 7))
    plt.title("Percentage of events" + title_add)
    plt.ylim(0, 100)

    plt.plot(sim_stats_df[x_col],
         sim_stats_df.percentage_satisfied,
         label = "satisfied",
         marker="o")

    plt.plot(sim_stats_df[x_col], 
         sim_stats_df.percentage_same_zone_trips,
         label = "same zone",
         marker="o")
    
    plt.plot(sim_stats_df[x_col], 
         sim_stats_df.percentage_not_same_zone_trips,
         label = "neighbor zone",
         marker="o")

    plt.plot(sim_stats_df[x_col],
         sim_stats_df.percentage_unsatisfied,
         label = "unsatisfied",
         marker="o")

    plt.plot(sim_stats_df[x_col], 
         sim_stats_df.percentage_deaths,
         label = "not enough energy",
         marker="o")
    
    plt.plot(sim_stats_df[x_col], 
         sim_stats_df.percentage_no_close_cars,
         label = "no available cars",
         marker="o")

    plt.xlabel(x_col)
    plt.ylabel("percentage of events")
    plt.legend()
    plt.savefig(os.path.join(figpath, figname + ".png"))
    plt.close()

def plot_param_cross_section (results_df, 
                              x_col, 
                              y_col, 
                              param_col,
                              figpath,
                              figname,
                              fixed_params_dict):

    plt.figure(figsize=(15, 7))
    plt.title(y_col + ", varying " + param_col + ", " + str(fixed_params_dict))
    plt.ylabel(y_col)
    plt.xlabel(x_col)
    for param_value in results_df[param_col].unique():
        group_df = results_df.loc\
            [(results_df[param_col] == param_value)]
        plt.plot(group_df[x_col], 
                 group_df[y_col], 
                 marker="o", 
                 label=param_col + "=" + str(param_value))
    
    plt.legend()
    plt.savefig(os.path.join(figpath, figname + ".png"))
#    plt.show()
    plt.close()

