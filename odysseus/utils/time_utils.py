import calendar

import numpy as np
import pandas as pd


def get_daytype_from_week_config(week_config, weekday):
    for daytype in week_config["week_slots"]:
        if weekday in week_config["week_slots"][daytype]:
            return daytype


def get_day_slot_from_week_config(week_config, hour):
    for daytype in week_config["week_slots"]:
        for day_slot in week_config["day_slots"][daytype]:
            if hour in week_config["day_slots"][daytype][day_slot]:
                return day_slot


def get_daytype_from_weekday(weekday):
    if weekday in [5, 6]:
        return "weekend"
    else:
        return "weekday"


def get_weekday_string_from_int(i):
    return list(calendar.day_abbr)[i]


def get_weekday_int_from_string(s):
    return list(calendar.day_abbr).index(s)


def get_time_group_columns(trips_df_norm):

    trips_df_norm = trips_df_norm.sort_values(by=["start_time"]).dropna()

    try:
        trips_df_norm.loc[:, "start_time"] = pd.to_datetime(trips_df_norm.start_time)
        trips_df_norm.loc[:, "end_time"] = pd.to_datetime(trips_df_norm.end_time)
    except:
        trips_df_norm.loc[:, "start_time"] = trips_df_norm.start_time
        trips_df_norm.loc[:, "end_time"] = trips_df_norm.end_time

    if "duration" not in trips_df_norm:
        trips_df_norm.loc[:, "duration"] = (
                trips_df_norm.end_time - trips_df_norm.start_time
        ).apply(lambda dt: dt.total_seconds())

    if "vehicle_id" in trips_df_norm.columns and "t_parking_before" not in trips_df_norm.columns:
        for vehicle, vehicle_df in trips_df_norm.groupby("vehicle_id"):
            trips_df_norm.loc[vehicle_df.index, "t_parking_before"] = (
                    vehicle_df.start_time - vehicle_df.end_time.shift(1)
            ).apply(lambda dt: dt.total_seconds())
            trips_df_norm.loc[vehicle_df.index, "t_parking_after"] = (
                    vehicle_df.start_time.shift(-1) - vehicle_df.end_time
            ).apply(lambda dt: dt.total_seconds())

    if "year" not in trips_df_norm:
        trips_df_norm.loc[:, "start_year"] = trips_df_norm.start_time.apply(lambda dt: dt.year)
        trips_df_norm.loc[:, "end_year"] = trips_df_norm.end_time.apply(lambda dt: dt.year)
        trips_df_norm.loc[:, "year"] = trips_df_norm.loc[:, "start_year"]
    if "month" not in trips_df_norm:
        trips_df_norm.loc[:, "start_month"] = trips_df_norm.start_time.apply(lambda dt: dt.month)
        trips_df_norm.loc[:, "end_month"] = trips_df_norm.end_time.apply(lambda dt: dt.month)
        trips_df_norm.loc[:, "month"] = trips_df_norm.loc[:, "start_month"]
    if "day" not in trips_df_norm:
        trips_df_norm.loc[:, "start_day"] = trips_df_norm.start_time.apply(lambda dt: dt.day)
        trips_df_norm.loc[:, "end_day"] = trips_df_norm.end_time.apply(lambda dt: dt.day)
        trips_df_norm.loc[:, "day"] = trips_df_norm.loc[:, "start_day"]

    if "start_hour" not in trips_df_norm:
        trips_df_norm.loc[:, "start_hour"] = trips_df_norm.start_time.apply(lambda d: d.hour).astype(int)

    if "end_hour" not in trips_df_norm:
        trips_df_norm.loc[:, "end_hour"] = trips_df_norm.end_time.apply(lambda d: d.hour).astype(int)

    trips_df_norm.loc[:, "start_weekday"] = trips_df_norm.start_time.apply(
        lambda d: get_weekday_string_from_int(d.weekday()))
    trips_df_norm.loc[:, "end_weekday"] = trips_df_norm.end_time.apply(
        lambda d: get_weekday_string_from_int(d.weekday()))

    # trips_df_norm.loc[:, "start_weekday_hour"] = trips_df_norm.start_time.apply(
    # 	lambda d: "_".join([str(get_weekday_string_from_int(d.weekday())), str(d.hour)])
    # )
    # trips_df_norm.loc[:, "end_weekday_hour"] = trips_df_norm.end_time.apply(
    # 	lambda d: "_".join([str(get_weekday_string_from_int(d.weekday())), str(d.hour)])
    # )

    trips_df_norm.loc[:, "start_daytype"] = trips_df_norm.start_weekday.apply(
        lambda w: "weekend" if get_weekday_int_from_string(w) in [5, 6] else "weekday"
    )
    trips_df_norm.loc[:, "end_daytype"] = trips_df_norm.end_weekday.apply(
        lambda w: "weekend" if get_weekday_int_from_string(w) in [5, 6] else "weekday"
    )

    # trips_df_norm.loc[:, "start_daytype_hour"] = trips_df_norm.start_time.apply(
    #     lambda d: "_".join([
    #         "weekend" if str(get_weekday_string_from_int(d.weekday())) in [5, 6] else "weekday",
    #         str(d.hour)
    #     ])
    # )
    # trips_df_norm.loc[:, "end_daytype_hour"] = trips_df_norm.end_time.apply(
    #     lambda d: "_".join([
    #         "weekend" if str(get_weekday_string_from_int(d.weekday())) in [5, 6] else "weekday",
    #         str(d.hour)
    #     ])
    # )

    # trips_df_norm.loc[:, "start_daymoment"] = pd.Series()
    # trips_df_norm.loc[trips_df_norm.start_hour.isin(range(0, 6)), "start_daymoment"] = "night"
    # trips_df_norm.loc[trips_df_norm.start_hour.isin(range(6, 12)), "start_daymoment"] = "morning"
    # trips_df_norm.loc[trips_df_norm.start_hour.isin(range(12, 18)), "start_daymoment"] = "afternoon"
    # trips_df_norm.loc[trips_df_norm.start_hour.isin(range(18, 24)), "start_daymoment"] = "evening"
    # trips_df_norm.loc[:, "end_daymoment"] = pd.Series()
    # trips_df_norm.loc[trips_df_norm.start_hour.isin(range(0, 6)), "end_daymoment"] = "night"
    # trips_df_norm.loc[trips_df_norm.start_hour.isin(range(6, 12)), "end_daymoment"] = "morning"
    # trips_df_norm.loc[trips_df_norm.start_hour.isin(range(12, 18)), "end_daymoment"] = "afternoon"
    # trips_df_norm.loc[trips_df_norm.start_hour.isin(range(18, 24)), "end_daymoment"] = "evening"
    #
    # trips_df_norm.loc[:, "start_daytype_daymoment"] = trips_df_norm.loc[:, ["start_daytype", "start_daymoment"]].apply(
    # 	lambda x: "_".join([x[0], x[1]]), axis=1
    # )

    return trips_df_norm


def get_grouped_aggfunc(df, group_cols, stats_col, aggfuncs):
    out_df = pd.DataFrame()
    s = df.groupby(group_cols)[stats_col]
    for aggfunc in aggfuncs:
        new_col_name = "_".join([aggfunc, stats_col])
        if aggfunc == "count":
            new_col_name = "_".join([aggfunc])
            out_s = s.count()
        elif aggfunc == "sum":
            out_s = s.sum()
        elif aggfunc == "mean":
            out_s = s.mean()
        elif aggfunc == "median":
            out_s = s.median()
        elif aggfunc == "min":
            out_s = s.min()
        elif aggfunc == "max":
            out_s = s.max()
        elif aggfunc == "std":
            out_s = s.std()
        out_df[new_col_name] = out_s
    return out_df


def get_resampled_aggfunc(df, freq, stats_col, aggfuncs):
    out_df = pd.DataFrame()
    s = df.set_index("start_time")[stats_col].resample(freq)
    for aggfunc in aggfuncs:
        new_col_name = "_".join([aggfunc, freq, stats_col])
        if aggfunc == "count":
            new_col_name = "_".join([aggfunc, freq])
            out_s = s.count().fillna(0.0).iloc[:, 0]
        elif aggfunc == "sum":
            out_s = s.sum()
        elif aggfunc == "mean":
            out_s = s.mean()
        elif aggfunc == "median":
            out_s = s.median()
        elif aggfunc == "min":
            out_s = s.min()
        elif aggfunc == "max":
            out_s = s.max()
        elif aggfunc == "std":
            out_s = s.std()
        out_df[new_col_name] = out_s
    return out_df


def get_grouped_resampled_count(df, group_cols, freq):
    grouped_resampled_df = pd.DataFrame(
        index=df.set_index("start_time").iloc[:, 0].resample(freq).count().index
    )
    for group, group_df in df.set_index("start_time").groupby(group_cols):
        grouped_resampled_df.loc[
            group_df.iloc[:, 0].resample(freq).count().index,
            group
        ] = group_df.iloc[:, 0].resample(freq).count()
    return grouped_resampled_df.fillna(0)


def get_grouped_resampled_count_aggfunc(df, group_cols, freq, aggfuncs):
    out_df = pd.DataFrame(index=df.groupby(group_cols).groups)
    for group, group_df in df.groupby(group_cols):
        group_df = group_df.reindex(df.index)
        s = group_df.set_index("start_time").iloc[:, 0].resample(freq).count().fillna(0.0)
        for aggfunc in aggfuncs:
            new_col_name = "_".join([aggfunc, "count", freq])
            if aggfunc == "sum":
                out_df.loc[group, new_col_name] = s.sum()
            elif aggfunc == "mean":
                out_df.loc[group, new_col_name] = s.mean()
            elif aggfunc == "median":
                out_df.loc[group, new_col_name] = s.median()
            elif aggfunc == "min":
                out_df.loc[group, new_col_name] = s.min()
            elif aggfunc == "max":
                out_df.loc[group, new_col_name] = s.max()
            elif aggfunc == "std":
                out_df.loc[group, new_col_name] = s.std()
    return out_df


def get_grouped_resampled_aggfunc(df, group_cols, freq, stats_col, aggfuncs):
    out_df = pd.DataFrame()
    for aggfunc in aggfuncs:
        new_col_name = "_".join([aggfunc, stats_col, freq])
        for group, group_df in df.set_index("start_time").groupby(group_cols):
            s = group_df[stats_col].resample(freq).sum()
            if aggfunc == "sum":
                out_df.loc[group, new_col_name] = s.sum()
            elif aggfunc == "mean":
                out_df.loc[group, new_col_name] = s.mean()
            elif aggfunc == "median":
                out_df.loc[group, new_col_name] = s.median()
            elif aggfunc == "min":
                out_df.loc[group, new_col_name] = s.min()
            elif aggfunc == "max":
                out_df.loc[group, new_col_name] = s.max()
            elif aggfunc == "std":
                out_df.loc[group, new_col_name] = s.std()
    return out_df


def reshape_time_grouped_signature(time_grouped_signatures):
    time_grouped_signatures["time_group"] = time_grouped_signatures.index.get_level_values(1)
    new_df = pd.DataFrame()
    for group, group_df in time_grouped_signatures.groupby("time_group"):
        group_df.columns = [col + "_" + group for col in group_df]
        new_df = pd.concat([new_df, group_df], axis=1)
    new_df["plate"] = new_df.index.get_level_values(0).values
    new_df = new_df.fillna(0).groupby("plate").sum()
    return new_df


def get_resampled_grouped_count_aggfunc(trips_df_norm, start_or_end, time_group_col, freq, aggfunc):
    time_grouped_hourly_count = pd.DataFrame()
    new_time_categorical_col = "_".join([start_or_end, time_group_col])
    new_count_col = "_".join([freq, start_or_end, "count"])

    time_grouped_hourly_count[new_time_categorical_col] = trips_df_norm.set_index(
        "_".join([start_or_end, "time"])
    ).resample(freq)[new_time_categorical_col].apply(
        lambda x: x.unique()[0] if len(x) > 0 else np.NaN
    ).fillna(0)

    time_grouped_hourly_count[new_count_col] = trips_df_norm.set_index(
        "_".join([start_or_end, "time"])
    ).resample(freq).count().iloc[:, 0]

    if aggfunc == "sum":
        return new_count_col, time_grouped_hourly_count.groupby(new_time_categorical_col)[new_count_col].sum().iloc[1:]
    if aggfunc == "mean":
        return new_count_col, time_grouped_hourly_count.groupby(new_time_categorical_col)[new_count_col].mean().iloc[1:]
    if aggfunc == "median":
        return new_count_col, time_grouped_hourly_count.groupby(new_time_categorical_col)[new_count_col].median().iloc[
                              1:]
    if aggfunc == "min":
        return new_count_col, time_grouped_hourly_count.groupby(new_time_categorical_col)[new_count_col].min().iloc[1:]
    if aggfunc == "max":
        return new_count_col, time_grouped_hourly_count.groupby(new_time_categorical_col)[new_count_col].max().iloc[1:]
    if aggfunc == "std":
        return new_count_col, time_grouped_hourly_count.groupby(new_time_categorical_col)[new_count_col].std().iloc[1:]


def get_resampled_grouped_aggfunc(trips_df_norm, start_or_end, stats_col, time_categorical_col, freq, aggfunc):
    time_grouped_hourly_stats = pd.DataFrame()

    new_time_categorical_col = "_".join([start_or_end, time_categorical_col])
    new_stats_col = "_".join([freq, start_or_end, stats_col, aggfunc])

    time_grouped_hourly_stats[new_time_categorical_col] = trips_df_norm.set_index(
        "_".join([start_or_end, "time"])
    ).resample(freq)[new_time_categorical_col].apply(
        lambda x: x.unique()[0] if len(x) > 0 else np.NaN
    ).fillna(0)

    time_grouped_hourly_stats[new_stats_col] = trips_df_norm.set_index(
        "_".join([start_or_end, "time"])
    ).resample(freq)[stats_col].sum()

    if aggfunc == "sum":
        return new_stats_col, time_grouped_hourly_stats.groupby(new_time_categorical_col)[new_stats_col].sum()
    if aggfunc == "mean":
        return new_stats_col, time_grouped_hourly_stats.groupby(new_time_categorical_col)[new_stats_col].mean()
    if aggfunc == "median":
        return new_stats_col, time_grouped_hourly_stats.groupby(new_time_categorical_col)[new_stats_col].median()
    if aggfunc == "min":
        return new_stats_col, time_grouped_hourly_stats.groupby(new_time_categorical_col)[new_stats_col].min()
    if aggfunc == "max":
        return new_stats_col, time_grouped_hourly_stats.groupby(new_time_categorical_col)[new_stats_col].max()
    if aggfunc == "std":
        return new_stats_col, time_grouped_hourly_stats.groupby(new_time_categorical_col)[new_stats_col].std()


def get_hourly_count_with_time_cols(trips_df_norm, start_or_end):
    time_grouped_hourly_count = pd.DataFrame()

    for time_categorical_col in ["hour", "weekday", "weekday_hour", "daymoment", "daytype"]:
        time_grouped_hourly_count["_".join([start_or_end, time_categorical_col])] = trips_df_norm.set_index(
            "_".join([start_or_end, "time"])
        ).resample("60Min")["_".join([start_or_end, time_categorical_col])].apply(
            lambda x: x.unique()[0] if len(x) > 0 else np.NaN
        ).fillna(0)

        time_grouped_hourly_count["_".join(["hourly", start_or_end, "count"])] = trips_df_norm.set_index(
            "_".join([start_or_end, "time"])
        ).resample("60Min").count().iloc[:, 0]

    return time_grouped_hourly_count


def get_hourly_mean_with_time_cols(df_norm, start_or_end, mean_col):
    time_grouped_hourly_mean = pd.DataFrame()

    for time_categorial_col in ["hour", "weekday", "weekday_hour", "daymoment", "daytype"]:
        time_grouped_hourly_mean["_".join([start_or_end, time_categorial_col])] = df_norm.set_index(
            "_".join([start_or_end, "time"])
        ).resample("60Min")["_".join([start_or_end, time_categorial_col])].apply(
            lambda x: x.unique()[0] if len(x) > 0 else np.NaN
        ).fillna(0)

        time_grouped_hourly_mean["_".join(["hourly", start_or_end, "mean"])] = df_norm.set_index(
            "_".join([start_or_end, "time"])
        ).resample("60Min")[mean_col].mean()

    return time_grouped_hourly_mean


def get_time_grouped_hourly_count(df_norm, start_or_end, which_df):
    time_grouped_hourly_count = pd.DataFrame()

    for time_categorial_col in ["hour", "weekday"]:
        time_grouped_hourly_count[time_categorial_col] = df_norm.set_index(
            "_".join([start_or_end, "time"])
        ).resample("60Min")["_".join([start_or_end, time_categorial_col])].apply(
            lambda x: x.unique()[0] if len(x) > 0 else np.NaN
        ).fillna(0)

        time_grouped_hourly_count["_".join([which_df, "hourly", start_or_end, "count"])] = df_norm.set_index(
            "_".join([start_or_end, "time"])
        ).resample("60Min").count().iloc[:, 0]

    return time_grouped_hourly_count


def get_time_grouped_hourly_mean(df_norm, start_or_end, which_df, mean_col):
    time_grouped_hourly_count = pd.DataFrame()

    for time_categorial_col in ["hour", "weekday"]:
        time_grouped_hourly_count[time_categorial_col] = df_norm.set_index(
            "_".join([start_or_end, "time"])
        ).resample("60Min")["_".join([start_or_end, time_categorial_col])].apply(
            lambda x: x.unique()[0] if len(x) > 0 else np.NaN
        ).fillna(0)

        time_grouped_hourly_count["_".join([which_df, "hourly", "mean"])] = df_norm.set_index(
            "_".join([start_or_end, "time"])
        ).resample("60Min")[mean_col].mean()

    return time_grouped_hourly_count


def update_req_time_info(booking_request):
    booking_request["date"] = booking_request["start_time"].date()
    booking_request["hour"] = booking_request["start_time"].hour
    booking_request["weekday"] = booking_request["start_time"].weekday()
    if booking_request["weekday"] in [5, 6]:
        booking_request["daytype"] = "weekend"
    else:
        booking_request["daytype"] = "weekday"
    return booking_request


def month_year_iter(start_month, start_year, end_month, end_year):
    """
	MonthYear Iterator. End month is included.
	:param start_month:
	:param start_year:
	:param end_month:
	:param end_year:
	:return:
	"""
    ym_start = 12 * start_year + start_month - 1
    ym_end = 12 * end_year + end_month
    for ym in range(ym_start, ym_end):
        y, m = divmod(ym, 12)
        yield y, m + 1


def weekday2vec(weekdays):
    """
    Weekdays to one-hot vector
    :param weekdays: Array of integer weekdays, where Monday is 0 and Sunday is 6.
    :return: Array of one-hot vectors, representing weekdays.
    """

    ret = []
    for i in weekdays:
        v = [0 for _ in range(7)]
        v[i] = 1
        if i >= 5:
            v.append(0)  # weekend
        else:
            v.append(1)  # weekday
        ret.append(v)
    return np.asarray(ret)
