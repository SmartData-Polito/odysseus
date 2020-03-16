import pandas as pd


def remap_plates (bookings):
	ass_dict = {
			sorted(bookings.plate.unique())[i]: i 
			for i in range(len(sorted(bookings.plate.unique())))
		}
	bookings.loc[:, "plate"] = bookings.plate.replace(ass_dict)
	return ass_dict, bookings


def get_bookings_dtypes(bookings):
	bookings["hour"] = bookings["hour"].astype(int)
	bookings["soc_delta"] = bookings["soc_delta"].astype(float)
	bookings["duration"] = bookings["duration"].astype(float)
	bookings["start_time"] = bookings["start_time"].apply(
		lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S')
	)
	bookings["end_time"] = bookings["end_time"].apply(
		lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S')
	)
	bookings["start_soc"] = bookings["start_soc"].astype(float)
	bookings["end_soc"] = bookings["end_soc"].astype(float)
	bookings.loc[bookings.end_soc > 100, "end_soc"] = 100
	return bookings


def get_bookings_dtypes(bookings):
	bookings["start_latitude"] = bookings["start_latitude"].astype(float)
	bookings["start_longitude"] = bookings["start_longitude"].astype(float)
	bookings["end_latitude"] = bookings["end_latitude"].astype(float)
	bookings["end_longitude"] = bookings["end_longitude"].astype(float)
	return get_bookings_dtypes(bookings)


def pre_process_time(df, col="start_time"):
	df.loc[:, col] = pd.to_datetime(df.start_time)
	df.loc[:, "month"] = df[col].apply(lambda d: d.month)
	df.loc[:, "weekday"] = df[col].apply(lambda d: d.weekday())
	df.loc[:, "day"] = df[col].apply(lambda d: d.day)
	df.loc[:, "hour"] = df[col].apply(lambda d: d.hour)
	df.loc[:, "minute"] = df[col].apply(lambda d: d.minute)
	df.loc[:, "duration"] = (df.end_time - df.start_time).apply(
		lambda x: float(x.seconds) / 60.0
	)
	df.loc[df.weekday.isin([5, 6]), "daytype"] = "weekend"
	df.loc[~df.weekday.isin([5, 6]), "daytype"] = "weekday"
	df.dropna(how="all", axis=1, inplace=True)
	df = df.sort_values(col)

	return df


def pre_process_bookings(bookings):
	bookings.start_time = pd.to_datetime(bookings.start_time, unit="s")
	bookings.end_time = pd.to_datetime(bookings.end_time, unit="s")
	bookings = pre_process_time(bookings)
	bookings["soc_delta"] = (bookings.end_soc - bookings.start_soc).astype(float)
	bookings_plates_dict, bookings = remap_plates(bookings)

	return bookings
