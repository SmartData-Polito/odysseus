import os.path
import datetime
import pandas as pd

from odysseus.path_config.path_config import root_data_path
from odysseus.utils.geospatial_utils import *
from odysseus.utils.time_utils import *
from odysseus.utils.bookings_utils import *


def generate_week_config(
        week_slots_type,
        day_slots_type,
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


def generate_hourly_od_count_dict(week_config, how="uniform"):
    hourly_od_count_dict = dict()
    if how == "uniform":
        for week_daytype in week_config["week_slots"].keys():
            hourly_od_count_dict[week_daytype] = {}
            for day_slot in week_config["day_slots"][week_daytype]:
                hour_min = int(week_config["day_slots"][week_daytype][day_slot].split("_")[0])
                hour_max = int(week_config["day_slots"][week_daytype][day_slot].split("_")[1])
                for hour in range(hour_min, hour_max):
                    hourly_od_count_dict[week_daytype][hour] = dict()
                    for origin in zone_ids:
                        hourly_od_count_dict[week_daytype][hour][origin] = {}
                        for destination in zone_ids:
                            hourly_od_count_dict[week_daytype][hour][origin][destination] = 3
    return hourly_od_count_dict


def get_hourly_od_df(
        hourly_count_dict, week_daytype, hour
):
    od_df = pd.DataFrame()
    for origin in zone_ids:
        for destination in zone_ids:
            od_df.loc[origin, destination] = hourly_count_dict[week_daytype][hour][origin][destination]
    return od_df


def generate_od_from_week_config(
        week_slots_type,
        day_slots_type,
        week_config,
        od_type,
        **kwargs
):
    od_matrices = dict()
    for week_daytype in week_config["week_slots"].keys():
        od_matrices[week_daytype] = {}
        for day_slot in week_config["day_slots"][week_daytype]:
            hour_min = int(week_config["day_slots"][week_daytype][day_slot].split("_")[0])
            hour_max = int(week_config["day_slots"][week_daytype][day_slot].split("_")[1])
            for hour in range(hour_min, hour_max):
                if od_type == "count":
                    assert "hourly_od_count_dict" in kwargs
                    od_matrices[week_daytype][str(hour)] = get_hourly_od_df(
                        kwargs["hourly_od_count_dict"], week_daytype, hour
                    )

    os.makedirs(os.path.join(root_data_path, city_name, "norm", "od_matrices", "my_data_source", ), exist_ok=True)
    for week_slot in od_matrices:
        for day_slot in od_matrices[week_slot]:
            od_matrices[week_slot][day_slot].to_csv(os.path.join(
                root_data_path, city_name, "norm", "od_matrices", "my_data_source",
                "_".join([str(week_slot), week_config["day_slots"][week_slot][day_slot]]) + ".csv"
            ))

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


def get_grid_indexes(grid_matrix, bookings, zone_ids):
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


def generate_trips_from_od(
        od_matrices, train_start_datetime, train_end_datetime, test_start_datetime, test_end_datetime
):
    train_booking_requests = pd.DataFrame(generate_booking_requests_list(
        train_start_datetime,
        train_end_datetime,
        od_matrices
    ))
    norm_trips_data_path = os.path.join(
        root_data_path, city_name, "norm", "trips", "my_data_source",
    )
    os.makedirs(norm_trips_data_path, exist_ok=True)

    test_booking_requests = pd.DataFrame(generate_booking_requests_list(
        test_start_datetime,
        test_end_datetime,
        od_matrices
    ))

    train_booking_requests = get_grid_indexes(grid_matrix, train_booking_requests, zone_ids)
    test_booking_requests = get_grid_indexes(grid_matrix, test_booking_requests, zone_ids)

    train_booking_requests.to_csv(os.path.join(
        norm_trips_data_path, "bookings_train.csv"
    ))
    test_booking_requests.to_csv(os.path.join(
        norm_trips_data_path, "bookings_test.csv"
    ))


week_config = generate_week_config(
    week_slots_type="weekday_weekend",
    day_slots_type="hours",
)
print(week_config)

grid_matrix = get_city_grid_as_matrix(
    (0, 0, 1500, 1500),
    500,
    "dummy_crs"
)
print(grid_matrix)

zone_ids = np.ravel(grid_matrix.values)

hourly_od_count_dict = generate_hourly_od_count_dict(week_config, "uniform")

od_matrices = generate_od_from_week_config(
    week_slots_type="weekday_weekend",
    day_slots_type="hours",
    week_config=week_config,
    od_type="count",
    hourly_od_count_dict=hourly_od_count_dict
)

city_name = "my_city_3X3"

generate_trips_from_od(
    od_matrices,
    datetime.datetime(2023, 1, 1, 0, 0, 1),
    datetime.datetime(2023, 1, 8, 0, 0, 1),
    datetime.datetime(2023, 1, 8, 0, 0, 1),
    datetime.datetime(2023, 1, 15, 0, 0, 1),
)
