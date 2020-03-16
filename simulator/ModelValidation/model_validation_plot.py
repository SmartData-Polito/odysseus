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

import seaborn as sns

from ModelValidation.model_validation_utils import get_plot_samples
from ModelValidation.model_validation_utils import get_grouped_reqs_count
from ModelValidation.model_validation_utils import get_day_moments
from ModelValidation.model_validation_utils import get_od_err_daymoments
from ModelValidation.model_validation_utils import get_od_err

def plot_ia_validation(ia_threshold, city, sim_reqs_eventG, trace_timeouts):

    eventG_ia_samples, traceB_ia_samples = \
        get_plot_samples(ia_threshold, sim_reqs_eventG, trace_timeouts)

    plt.figure(figsize=(9, 9))
    plt.title("Q-Q plot of interarrival times")
    plt.scatter(eventG_ia_samples, traceB_ia_samples)
    plt.plot(eventG_ia_samples.sort_values(),
             eventG_ia_samples.sort_values())
    plt.xlabel("sim ia times")
    plt.ylabel("trace ia times [s]")
    plt.savefig("./Figures/" + city + "/validation/qq-" + str(ia_threshold))
    # plt.show()
    plt.close()

def plot_tot_reqs_count(group_col, normed, city, sim_reqs_eventG, sim_reqs_traceB):

    sim_reqs_eventG_count, sim_reqs_traceB_count = \
        get_grouped_reqs_count(group_col, sim_reqs_eventG, sim_reqs_traceB)

    if normed:
        title = "normalised"
        figfilename = "_".join([group_col, "reqs-count-norm"])
        sim_reqs_eventG_count = \
            sim_reqs_eventG_count / len(sim_reqs_eventG)
        sim_reqs_traceB_count = \
            sim_reqs_traceB_count / len(sim_reqs_traceB)
    else:
        title = ""
        figfilename = "_".join([group_col, "reqs-count"])

    pd.concat([sim_reqs_eventG_count,
               sim_reqs_traceB_count], axis=1) \
        .plot.bar(figsize=(15, 7))
    plt.title(title + " count of booking requests by " + group_col)
    plt.xlabel(group_col)
    plt.ylabel("fraction of booking requests")
    plt.legend()
    plt.savefig("./Figures/" + city + "/validation/" + figfilename)
    # plt.show()
    plt.close()


def plot_tot_reqs_count_err(group_col, normed, city, sim_reqs_eventG, sim_reqs_traceB):
    sim_reqs_eventG_count = \
        (sim_reqs_eventG \
         .sort_values("start_time") \
         .groupby(group_col).origin_id.count())

    sim_reqs_traceB_count = \
        (sim_reqs_traceB \
         .sort_values("start_time") \
         .groupby(group_col).origin_id.count())

    if normed:
        title = "normalised"
        figfilename = "_".join([group_col, "reqs-count-err-norm"])
        sim_reqs_eventG_count = \
            sim_reqs_eventG_count / len(sim_reqs_eventG)
        sim_reqs_traceB_count = \
            sim_reqs_traceB_count / len(sim_reqs_traceB)
    else:
        title = ""
        figfilename = "_".join([group_col, "reqs-count"])

    # print("Total error:",
    #       (sim_reqs_eventG_count - sim_reqs_traceB_count).abs().sum())

    (sim_reqs_eventG_count - sim_reqs_traceB_count).abs() \
        .plot.bar(figsize=(15, 7))
    plt.title(title + " count error by " + group_col)
    plt.xlabel(group_col)
    plt.ylabel("% booking requests")
    plt.savefig("./Figures/" + city + "/validation/" + figfilename)
    # plt.show()
    plt.close()


def plot_tot_reqs_count_err_agg(group_col, normed, city, sim_reqs_eventG, sim_reqs_traceB):
    sim_reqs_eventG_count = \
        (sim_reqs_eventG \
         .sort_values("start_time") \
         .groupby(["daytype", "hour"]).origin_id.count())

    sim_reqs_traceB_count = \
        (sim_reqs_traceB \
         .sort_values("start_time") \
         .groupby(["daytype", "hour"]).origin_id.count())

    if normed:
        title = "normalised"
        figfilename = "_".join(["reqs-count-err-norm"])
        sim_reqs_eventG_count = \
            sim_reqs_eventG_count
        sim_reqs_traceB_count = \
            sim_reqs_traceB_count
    else:
        title = ""
        figfilename = "_".join(["reqs-count-err"])

    # print("Total error:",
    #       (sim_reqs_eventG_count - sim_reqs_traceB_count).abs().sum())

    errs_df = pd.DataFrame()
    for daytype in ["weekday", "weekend"]:
        errs_df[daytype] = \
            (sim_reqs_eventG_count.loc[daytype] \
            - sim_reqs_traceB_count.loc[daytype]) \
                / sim_reqs_traceB_count.sum()

    (errs_df).abs() \
        .plot.bar(figsize=(15, 7))
    plt.title(title + " count error by hour and daytype")
    plt.xlabel("hour")
    plt.ylabel("% booking requests")
    plt.savefig("./Figures/" + city + "/validation/" + figfilename)
    # plt.show()
    plt.close()


def plot_regr_qq_sns(city, sim_reqs_eventG, trace_timeouts):

    eventG_ia_samples, traceB_ia_samples = \
        get_plot_samples(1000, sim_reqs_eventG, trace_timeouts)

    sns_df = pd.concat([pd.Series(eventG_ia_samples.sort_values().reset_index()["ia_timeout"],
                                  name="ia_eventG"),
                        pd.Series(traceB_ia_samples.sort_values().reset_index()["ia_timeout"],
                                  name="ia_traceB")], axis=1)

    sns.jointplot("ia_eventG", "ia_traceB", sns_df, kind="reg", height=9)
    plt.plot(eventG_ia_samples, eventG_ia_samples, color="black", label="bisector")
    plt.title("Regression and Q-Q plots for ia times model, with sample distributions")
    plt.legend()
    plt.savefig("Figures/" + city + "/validation/reg1000_sns.png")
    sns.despine()
    # plt.show()
    plt.close()

def plot_od_err (city, grid, sim_reqs_eventG, sim_reqs_traceB):

    sim_reqs_eventG, sim_reqs_traceB = \
        get_day_moments(sim_reqs_eventG, sim_reqs_traceB)

    grid = get_od_err_daymoments(grid, sim_reqs_eventG, sim_reqs_traceB)

    fig, axs = plt.subplots(2, 2, figsize=(12, 12))

    i = 0
    j = 0

    for daymoment in ["night", "morning", "afternoon", "evening"]:

        grid.dropna(subset=["od_count_diff_" + daymoment]) \
            .plot(column="od_count_diff_" + daymoment, ax=axs[i][j], legend=True)
        axs[i][j].set_title("od balance diff heatmap " + daymoment)
        axs[i][j].set_xlabel("longitude")
        axs[i][j].set_ylabel("latitude")

        if j == 1:
            i = (i + 1) % 2
        j = (j + 1) % 2

    plt.savefig("./Figures/" + city + "/validation/sp_err_daymoments.png")
    # plt.show()
    plt.close()

    grid = get_od_err(grid, sim_reqs_eventG, sim_reqs_traceB)
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    grid.plot(column="od_count_diff", ax=ax, legend=True)

    plt.savefig("./Figures/" + city + "/validation/sp_err.png")
    # plt.show()
    plt.close()
