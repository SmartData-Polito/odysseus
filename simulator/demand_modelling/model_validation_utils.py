import pandas as pd

def get_plot_samples(ia_threshold, sim_reqs_eventG, trace_timeouts):

    up_threshold = trace_timeouts.quantile(q=0.999).mean()
    filtered_reqs_eventG = sim_reqs_eventG.ia_timeout \
        [(sim_reqs_eventG.ia_timeout < up_threshold)]
    filtered_reqs_traceB = trace_timeouts \
        [(trace_timeouts < up_threshold)]

    n_samples = min([len(filtered_reqs_eventG), len(filtered_reqs_traceB)])
    # n_samples = 5000

    eventG_ia_samples = \
        filtered_reqs_eventG \
            .sample(n_samples).sort_values()

    traceB_ia_samples = \
        filtered_reqs_traceB \
            .sample(n_samples).sort_values()

    return eventG_ia_samples, traceB_ia_samples

def get_grouped_reqs_count(group_col, sim_reqs_eventG, sim_reqs_traceB):

    sim_reqs_eventG_count = \
        pd.Series((sim_reqs_eventG\
                   .sort_values("start_time")\
                   .groupby(group_col).origin_id.count()), name="eventG")

    sim_reqs_traceB_count = \
        pd.Series((sim_reqs_traceB\
                   .sort_values("start_time")\
                   .groupby(group_col).origin_id.count()), name="traceB")

    return sim_reqs_eventG_count, sim_reqs_traceB_count

def get_tot_zones_errs (sim_reqs_eventG, sim_reqs_traceB):

    traceB_origin_count = sim_reqs_traceB.origin_id.value_counts() / len(sim_reqs_traceB)
    eventG_origin_count = sim_reqs_eventG.origin_id.value_counts() / len(sim_reqs_eventG)
    zones_origin_errs = (traceB_origin_count - eventG_origin_count)

    traceB_destination_count = sim_reqs_traceB.destination_id.value_counts() / len(sim_reqs_traceB)
    eventG_destination_count = sim_reqs_eventG.destination_id.value_counts() / len(sim_reqs_eventG)
    zones_destination_errs = (traceB_destination_count - eventG_destination_count)

    origin_tot_err = zones_origin_errs.abs().max()
    destination_tot_err = zones_destination_errs.abs().max()
    print (origin_tot_err, destination_tot_err)

    return zones_origin_errs, zones_destination_errs

def get_grouped_zones_errs (sim_reqs_eventG, sim_reqs_traceB, group_col):

    traceB_origin_count_grouped = \
        sim_reqs_traceB.groupby(group_col).origin_id.value_counts()\
        / sim_reqs_traceB.groupby(group_col).origin_id.sum()
    eventG_origin_count_grouped = \
        sim_reqs_eventG.groupby(group_col).origin_id.value_counts()\
        / sim_reqs_eventG.groupby(group_col).origin_id.sum()

    traceB_destination_count_grouped = \
        sim_reqs_traceB.groupby(group_col).destination_id.value_counts()\
        / sim_reqs_traceB.groupby(group_col).destination_id.sum()
    eventG_destination_count_grouped = \
        sim_reqs_eventG.groupby(group_col).destination_id.value_counts()\
        / sim_reqs_eventG.groupby(group_col).destination_id.sum()

    origin_tot_err = (traceB_origin_count_grouped - eventG_origin_count_grouped)
    destination_tot_err = (traceB_destination_count_grouped - eventG_destination_count_grouped)
    # print (origin_tot_err, destination_tot_err)

def get_double_grouped_zones_errs (sim_reqs_eventG, sim_reqs_traceB, group_cols):

    traceB_origin_count_grouped = \
        sim_reqs_traceB.groupby(group_cols).origin_id.value_counts()
    eventG_origin_count_grouped = \
        sim_reqs_eventG.groupby(group_cols).origin_id.value_counts()
    origin_tot_err =  ((traceB_origin_count_grouped - eventG_origin_count_grouped).abs().sum()\
           / len(sim_reqs_traceB))

    traceB_destination_count_grouped = \
        sim_reqs_traceB.groupby(group_cols).destination_id.value_counts()
    eventG_destination_count_grouped = \
        sim_reqs_eventG.groupby(group_cols).destination_id.value_counts()
    destination_tot_err =  ((traceB_destination_count_grouped - eventG_destination_count_grouped).abs().sum()\
           / len(sim_reqs_traceB))

    # print (origin_tot_err, destination_tot_err)

def get_day_moments (sim_reqs_eventG, sim_reqs_traceB):

    sim_reqs_eventG.loc \
        [(sim_reqs_eventG.hour.isin([23, 0, 1, 2, 3, 4])), "daymoment"] = "night"

    sim_reqs_eventG.loc \
        [(sim_reqs_eventG.hour.isin([5, 6, 7, 8, 9, 10, 11, 12])), "daymoment"] = "morning"

    sim_reqs_eventG.loc \
        [(sim_reqs_eventG.hour.isin([13, 14, 15, 16, 17, 18])), "daymoment"] = "afternoon"

    sim_reqs_eventG.loc \
        [(sim_reqs_eventG.hour.isin([19, 20, 21, 22])), "daymoment"] = "evening"

    sim_reqs_traceB.loc \
        [(sim_reqs_traceB.hour.isin([23, 0, 1, 2, 3, 4])), "daymoment"] = "night"

    sim_reqs_traceB.loc \
        [(sim_reqs_traceB.hour.isin([5, 6, 7, 8, 9, 10, 11, 12])), "daymoment"] = "morning"

    sim_reqs_traceB.loc \
        [(sim_reqs_traceB.hour.isin([13, 14, 15, 16, 17, 18])), "daymoment"] = "afternoon"

    sim_reqs_traceB.loc \
        [(sim_reqs_traceB.hour.isin([19, 20, 21, 22])), "daymoment"] = "evening"

    return sim_reqs_eventG, sim_reqs_traceB

def get_od_err_daymoments(grid, sim_reqs_eventG, sim_reqs_traceB):

    for daymoment in ["night", "morning", "afternoon", "evening"]:

        grid["eventG_origin_count_" + daymoment] = \
            sim_reqs_eventG[sim_reqs_eventG.daymoment == daymoment] \
                .origin_id.value_counts() \
            / len(sim_reqs_eventG[sim_reqs_eventG.daymoment == daymoment])

        grid["traceB_origin_count_" + daymoment] = \
            sim_reqs_traceB[sim_reqs_traceB.daymoment == daymoment] \
                .origin_id.value_counts() \
            / len(sim_reqs_eventG[sim_reqs_eventG.daymoment == daymoment])

        grid["eventG_destination_count_" + daymoment] = \
            sim_reqs_eventG[sim_reqs_eventG.daymoment == daymoment] \
                .destination_id.value_counts() \
            / len(sim_reqs_eventG[sim_reqs_eventG.daymoment == daymoment])

        grid["traceB_destination_count_" + daymoment] = \
            sim_reqs_traceB[sim_reqs_traceB.daymoment == daymoment] \
                .destination_id.value_counts() \
            / len(sim_reqs_eventG[sim_reqs_eventG.daymoment == daymoment])

        grid["origin_count_diff_" + daymoment] = \
            (grid["eventG_origin_count_" + daymoment] \
            - grid["traceB_origin_count_" + daymoment]).abs()

        grid["destinations_od_count_diff_" + daymoment] = \
            (grid["eventG_destination_count_" + daymoment] \
            - grid["traceB_destination_count_" + daymoment]).abs()

        current_grid = grid.loc \
            [:, ["origin_count_diff_" + daymoment,
                 "destinations_od_count_diff_" + daymoment]] \
            .dropna(how="all").fillna(0)

        grid["od_count_diff_" + daymoment] = \
            current_grid["origin_count_diff_" + daymoment] \
            + current_grid["destinations_od_count_diff_" + daymoment]

        # print(grid["od_count_diff_" + daymoment].sum())

    return grid

def get_od_err(grid, sim_reqs_eventG, sim_reqs_traceB):

    grid["eventG_origin_count"] = \
        sim_reqs_eventG.origin_id.value_counts() \
        / len(sim_reqs_eventG)

    grid["traceB_origin_count"] = \
        sim_reqs_traceB.origin_id.value_counts() \
        / len(sim_reqs_eventG)

    grid["eventG_destination_count"] = \
        sim_reqs_eventG.destination_id.value_counts() \
        / len(sim_reqs_eventG)

    grid["traceB_destination_count"] = \
        sim_reqs_traceB.destination_id.value_counts() \
        / len(sim_reqs_eventG)

    grid["origin_count_diff"] = \
        (grid["eventG_origin_count" ] \
        - grid["traceB_origin_count"]).abs()

    grid["destinations_od_count_diff"] = \
        (grid["eventG_destination_count"] \
        - grid["traceB_destination_count"]).abs()

    current_grid = grid.loc \
        [:, ["origin_count_diff",
             "destinations_od_count_diff"]] \
        .dropna(how="all").fillna(0)

    grid["od_count_diff"] = \
        current_grid["origin_count_diff"] \
        + current_grid["destinations_od_count_diff"]

    return grid
