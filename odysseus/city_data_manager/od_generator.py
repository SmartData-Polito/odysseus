import os.path
import datetime
import pandas as pd

from odysseus.path_config.path_config import root_data_path
from odysseus.utils.geospatial_utils import *
from odysseus.utils.time_utils import *
from odysseus.utils.bookings_utils import *


def generate_week_config(
        week_slots_type="weekday_weekend",
        day_slots_type="hours",
        week_slots_config=None,
        day_slots_config=None
):
    week_config = dict()
    if week_slots_type == "weekday_weekend" and day_slots_type == "hours":
        week_config["week_slots"] = dict()
        week_config["week_slots"]["weekday"] = [w for w in range(0, 6)]
        week_config["week_slots"]["weekend"] = [6, 7]
        week_config["day_slots"] = dict()
        week_config["day_slots"]["weekday"] = dict()
        week_config["day_slots"]["weekend"] = dict()
        for h in range(24):
            week_config["day_slots"]["weekday"][str(h)] = str(h) + "_" + str(h+1)
            week_config["day_slots"]["weekend"][str(h)] = str(h) + "_" + str(h+1)

    return week_config


def get_od_df(hourly_count_dict):
    od_df = pd.DataFrame()
    for week_daytype in week_config["week_slots"].keys():
        for day_slot in week_config["day_slots"][week_daytype]:
            for origin in zone_ids:
                for destination in zone_ids:
                    od_df.loc[origin, destination] = hourly_count_dict[week_daytype][day_slot][origin][destination]
    return od_df


def generate_od_from_week_config(
        week_config,
        od_type,
        **kwargs
):
    od_matrices = dict()
    for week_daytype in week_config["week_slots"].keys():
        od_matrices[week_daytype] = {}
        for day_slot in week_config["day_slots"][week_daytype]:
            if od_type == "count":
                assert "hourly_count_dict" in kwargs
                od_matrices[week_daytype][day_slot] = get_od_df(kwargs["hourly_count_dict"])
    return od_matrices


def generate_booking_requests_list(start_datetime, end_datetime, od_matrices):
    booking_requests_list = list()
    current_datetime = start_datetime
    print(current_datetime)
    current_hour = current_datetime.hour
    current_weekday = current_datetime.weekday()
    current_daytype = get_daytype_from_weekday(current_weekday)
    seconds_spent = 0
    while current_datetime < end_datetime:
        for o_id in od_matrices[current_daytype][str(current_hour)].index:
            for d_id in od_matrices[current_daytype][str(current_hour)].columns:
                n_bookings_to_generate = int(od_matrices[current_daytype][str(current_hour)].loc[o_id, d_id])
                if n_bookings_to_generate:
                    cum_timeout = 0
                    timeout_sec = 3600 / n_bookings_to_generate
                    for booking_request_to_generate in range(n_bookings_to_generate):
                        booking_request = create_booking_request_dict(
                            timeout_sec, current_datetime + datetime.timedelta(seconds=cum_timeout),
                            o_id, d_id
                        )
                        booking_request["end_time"] = current_datetime + datetime.timedelta(seconds=cum_timeout) + \
                                                      datetime.timedelta(seconds=15*60)
                        booking_request["origin_i"] = od_matrices[current_daytype][str(current_hour)]
                        cum_timeout += timeout_sec
                        booking_requests_list.append(booking_request)
                        seconds_spent += timeout_sec
        current_datetime += datetime.timedelta(seconds=3600)
        current_hour = current_datetime.hour
        current_weekday = current_datetime.weekday()
        current_daytype = get_daytype_from_weekday(current_weekday)

    return booking_requests_list


week_config = generate_week_config()
print(week_config)

grid_matrix = get_city_grid_as_matrix((0, 0, 1000, 1000), 500, "dummy_crs")
print(grid_matrix)

zone_ids = np.ravel(grid_matrix.values)

hourly_count_dict = dict()
for week_daytype in week_config["week_slots"].keys():
    hourly_count_dict[week_daytype] = {}
    for day_slot in week_config["day_slots"][week_daytype]:
        hourly_count_dict[week_daytype][day_slot] = dict()
        for origin in zone_ids:
            hourly_count_dict[week_daytype][day_slot][origin] = {}
            for destination in zone_ids:
                hourly_count_dict[week_daytype][day_slot][origin][destination] = 3

od_matrices = generate_od_from_week_config(week_config, "count", hourly_count_dict=hourly_count_dict)

os.makedirs(os.path.join(root_data_path, "my_city", "norm", "od_matrices", "my_data_source",), exist_ok=True)
for week_slot in od_matrices:
    for day_slot in od_matrices[week_slot]:
        od_matrices[week_slot][day_slot].to_csv(os.path.join(
            root_data_path, "my_city", "norm", "od_matrices", "my_data_source",
            "_".join([str(week_slot), week_config["day_slots"][week_slot][day_slot]]) + ".csv"
        ))


train_booking_requests = pd.DataFrame(generate_booking_requests_list(
    datetime.datetime(2023, 1, 1, 0, 0, 1),
    datetime.datetime(2023, 1, 8, 0, 0, 1),
    od_matrices
))
print(train_booking_requests.shape)
norm_trips_data_path = os.path.join(
    root_data_path, "my_city", "norm", "trips", "my_data_source",
)
os.makedirs(norm_trips_data_path, exist_ok=True)


test_booking_requests = pd.DataFrame(generate_booking_requests_list(
    datetime.datetime(2023, 1, 8, 0, 0, 1),
    datetime.datetime(2023, 1, 15, 1, 0, 1),
    od_matrices
))
print(test_booking_requests.shape)


def get_grid_indexes(bookings, zone_ids):
    zone_coords_dict = {}
    for j in grid_matrix.columns:
        for i in grid_matrix.index:
            zone_coords_dict[grid_matrix.iloc[i, j]] = (i, j)

    for zone in zone_ids:
        bookings.loc[bookings.origin_id == zone, "origin_i"] = zone_coords_dict[zone][0]
        bookings.loc[bookings.origin_id == zone, "origin_j"] = zone_coords_dict[zone][1]
        bookings.loc[bookings.destination_id == zone, "destination_i"] = zone_coords_dict[zone][0]
        bookings.loc[bookings.destination_id == zone, "destination_j"] = zone_coords_dict[zone][1]
    return bookings


train_booking_requests = get_grid_indexes(train_booking_requests, zone_ids)
test_booking_requests = get_grid_indexes(test_booking_requests, zone_ids)

train_booking_requests.to_csv(os.path.join(
    norm_trips_data_path, "bookings_train.csv"
))
test_booking_requests.to_csv(os.path.join(
    norm_trips_data_path, "bookings_test.csv"
))
