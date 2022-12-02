import datetime
import pandas as pd
import numpy as np


def get_start_end_duration(bookings, timezone, random_seconds=0):

    bookings["random_seconds_start"] = np.random.uniform(-random_seconds, random_seconds, len(bookings))

    bookings.start_time = pd.to_datetime(
        bookings.start_time, utc=True
    ) + bookings.random_seconds_start.apply(
        lambda sec: datetime.timedelta(seconds=sec)
    )

    bookings["random_seconds_end"] = np.random.uniform(random_seconds, 2 * random_seconds, len(bookings))

    bookings.end_time = pd.to_datetime(
        bookings.end_time, utc=True
    ) + bookings.random_seconds_end.apply(
        lambda sec: datetime.timedelta(seconds=sec)
    )

    bookings["start_time"] = bookings["start_time"].dt.tz_convert(timezone)
    bookings["end_time"] = bookings["end_time"].dt.tz_convert(timezone)

    bookings.loc[:, "duration"] = (
            bookings.end_time - bookings.start_time
    ).apply(lambda x: x.total_seconds())

    # TODO -> check different behaviors with additional time columns
    # bookings = get_time_group_columns(bookings)
    bookings["hour"] = bookings.start_hour
    bookings["daytype"] = bookings.start_daytype
    bookings["date"] = bookings.start_time.apply(lambda d: d.date())

    bookings = bookings.sort_values("start_time")
    bookings.loc[:, "ia_timeout"] = (
            bookings.start_time - bookings.start_time.shift()
    ).apply(lambda x: x.total_seconds()).abs().fillna(10)
    bookings = bookings.loc[bookings.ia_timeout >= 0]

    return bookings
