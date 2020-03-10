import pandas as pd


def get_time_group_columns (trips_df_norm):

	trips_df_norm.sort_values(by=["start_time"], inplace=True)

	trips_df_norm.start_time = pd.to_datetime(trips_df_norm.start_time, utc=True)
	trips_df_norm.end_time = pd.to_datetime(trips_df_norm.end_time, utc=True)
	trips_df_norm["year"] = trips_df_norm.start_time.apply(
		lambda dt: dt.year
	)
	trips_df_norm["month"] = trips_df_norm.start_time.apply(
		lambda dt: dt.month
	)
	trips_df_norm["start_hour"] = trips_df_norm.start_time.apply(lambda d: d.hour).astype(int)
	trips_df_norm["end_hour"] = trips_df_norm.end_time.apply(lambda d: d.hour).astype(int)

	trips_df_norm["start_weekday"] = trips_df_norm.start_time.apply(lambda d: d.weekday)
	trips_df_norm["end_weekday"] = trips_df_norm.end_time.apply(lambda d: d.weekday)

	trips_df_norm["start_weekend"] = trips_df_norm.start_weekday.apply(lambda w: w in [5, 6]).fillna(False)
	trips_df_norm["end_weekend"] = trips_df_norm.end_weekday.apply(lambda w: w in [5, 6]).fillna(False)

	trips_df_norm["start_daymoment"] = pd.Series()
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(0,7)), "start_daymoment"] = "night"
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(7,13)), "start_daymoment"] = "morning"
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(13,19)), "start_daymoment"] = "afternoon"
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(19,24)), "start_daymoment"] = "evening"
	trips_df_norm["end_daymoment"] = pd.Series()
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(0, 7)), "end_daymoment"] = "night"
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(7, 13)), "end_daymoment"] = "morning"
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(13, 19)), "end_daymoment"] = "afternoon"
	trips_df_norm.loc[trips_df_norm.start_hour.isin(range(19, 24)), "end_daymoment"] = "evening"

	return trips_df_norm


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
