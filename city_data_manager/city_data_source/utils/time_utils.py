import pandas as pd
import numpy as np


def get_time_group_columns (trips_df_norm):

	trips_df_norm = trips_df_norm.sort_values(by=["start_time"])

	trips_df_norm.start_time = pd.to_datetime(trips_df_norm.start_time, utc=True)
	trips_df_norm.end_time = pd.to_datetime(trips_df_norm.end_time, utc=True)
	trips_df_norm["duration"] = (trips_df_norm.end_time - trips_df_norm.start_time).apply(
		lambda dt: dt.total_seconds()
	)
	trips_df_norm.loc[:, "year"] = trips_df_norm.start_time.apply(
		lambda dt: dt.year
	)
	trips_df_norm.loc[:, "month"] = trips_df_norm.start_time.apply(
		lambda dt: dt.month
	)
	trips_df_norm.loc[:, "start_hour"] = trips_df_norm.start_time.apply(lambda d: d.hour).astype(int)
	trips_df_norm.loc[:, "end_hour"] = trips_df_norm.end_time.apply(lambda d: d.hour).astype(int)

	trips_df_norm.loc[:, "start_weekday"] = trips_df_norm.start_time.apply(lambda d: d.weekday)
	trips_df_norm.loc[:, "end_weekday"] = trips_df_norm.end_time.apply(lambda d: d.weekday)

	trips_df_norm.loc[:, "start_weekend"] = trips_df_norm.start_weekday.apply(lambda w: w in [5, 6]).fillna(False)
	trips_df_norm.loc[:, "end_weekend"] = trips_df_norm.end_weekday.apply(lambda w: w in [5, 6]).fillna(False)

	trips_df_norm.loc[:, "start_daymoment"] = pd.Series()
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(0, 7)), "start_daymoment"] = "night"
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(7, 13)), "start_daymoment"] = "morning"
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(13, 19)), "start_daymoment"] = "afternoon"
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(19, 24)), "start_daymoment"] = "evening"
	trips_df_norm.loc[:, "end_daymoment"] = pd.Series()
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(0, 7)), "end_daymoment"] = "night"
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(7, 13)), "end_daymoment"] = "morning"
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(13, 19)), "end_daymoment"] = "afternoon"
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(19, 24)), "end_daymoment"] = "evening"

	return trips_df_norm


def get_time_grouped_hourly_count(df_norm, start_or_end, which_df):

	time_grouped_hourly_count = pd.DataFrame()

	for time_categorial_col in ["hour", "weekday", "daymoment", "weekend"]:

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

	for time_categorial_col in ["hour", "weekday", "daymoment", "weekend"]:

		time_grouped_hourly_count[time_categorial_col] = df_norm.set_index(
			"_".join([start_or_end, "time"])
		).resample("60Min")["_".join([start_or_end, time_categorial_col])].apply(
			lambda x: x.unique()[0] if len(x) > 0 else np.NaN
		).fillna(0)

		time_grouped_hourly_count["_".join([which_df, "hourly", "mean"])] = df_norm.set_index(
			"_".join([start_or_end, "time"])
		).resample("60Min")[mean_col].mean()

	return time_grouped_hourly_count


def get_grouped_resampled_count (df, group_cols, freq):
	grouped_resampled_df = pd.DataFrame(
		index=df.set_index("start_time").iloc[:, 0].resample(freq).count().index
	)
	for group, group_df in df.set_index("start_time").groupby(group_cols):
		grouped_resampled_df.loc[
			group_df.iloc[:, 0].resample(freq).count().index,
			group
		] = group_df.iloc[:, 0].resample(freq).count()
	return grouped_resampled_df.fillna(0)


def get_grouped_resampled_agg_stats (df, group_cols, freq, stats_col, aggfunc):
	new_col_name = "_".join([aggfunc, stats_col])
	s = pd.Series()
	for group, group_df in df.set_index("start_time").groupby(group_cols):
		if aggfunc == "mean":
			s.loc[group] = group_df[stats_col].resample(freq).sum().mean()
		elif aggfunc == "max":
			s.loc[group] = group_df[stats_col].resample(freq).sum().max()
	return new_col_name, s
