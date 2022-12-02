import os
import datetime
import pandas as pd
import numpy as np

from odysseus.utils.time_utils import get_daytype_from_week_config, get_day_slot_from_week_config
from odysseus.utils.bookings_utils import create_booking_request_dict
from odysseus.utils.bookings_utils import get_grid_indexes
from odysseus.path_config.path_config import root_data_path


def generate_booking_requests_list(
        od_matrices, week_config, distance_matrix, start_datetime, end_datetime,
        requests_rate_factor,
        avg_speed_kmh_mean,
        max_duration,
        fixed_driving_distance
):

    booking_requests_list = list()
    current_datetime = start_datetime
    current_hour = current_datetime.hour
    # TODO -> verify hour int vs string
    current_weekday = current_datetime.weekday()
    current_daytype = get_daytype_from_week_config(week_config, current_weekday)
    current_day_slot_str = get_day_slot_from_week_config(week_config, current_hour)

    while current_datetime < end_datetime:

        for o_id in od_matrices[current_daytype][current_day_slot_str].index:
            for d_id in od_matrices[current_daytype][current_day_slot_str].columns:

                n_bookings_to_generate = int(
                    od_matrices[current_daytype][current_day_slot_str].loc[o_id, d_id] * requests_rate_factor
                )

                if n_bookings_to_generate:
                    for booking_request_to_generate in range(n_bookings_to_generate):
                        booking_req_start_datetime = current_datetime + datetime.timedelta(
                            seconds=np.random.uniform(1, 60)
                        )
                        booking_request = create_booking_request_dict(
                            week_config, 0,
                            booking_req_start_datetime,
                            o_id, d_id, distance_matrix,
                            avg_speed_kmh_mean,
                            max_duration,
                            fixed_driving_distance
                        )
                        booking_requests_list.append(booking_request)

        current_datetime += datetime.timedelta(seconds=3600)
        current_hour = current_datetime.hour
        current_day_slot_str = get_day_slot_from_week_config(week_config, current_hour)
        current_weekday = current_datetime.weekday()
        current_daytype = get_daytype_from_week_config(week_config, current_weekday)

    booking_requests_df = pd.DataFrame(booking_requests_list).sort_values("start_time").reset_index()

    booking_requests_df["ia_timeout"] = (
        booking_requests_df.start_time - booking_requests_df.start_time.shift(1)
    ).apply(lambda td: abs(td.total_seconds()))

    booking_requests_df.at[0, "ia_timeout"] = (
        booking_requests_df.at[0, "start_time"] - start_datetime
    ).total_seconds()

    return booking_requests_df.to_dict("records")


def generate_trips_from_od(
        city_name, od_matrices, week_config, grid_matrix, zone_ids, distance_matrix,
        train_start_datetime, train_end_datetime, test_start_datetime, test_end_datetime
):

    train_booking_requests = pd.DataFrame(generate_booking_requests_list(
        od_matrices,
        week_config,
        distance_matrix,
        train_start_datetime,
        train_end_datetime,
        requests_rate_factor=1
    ))
    norm_trips_data_path = os.path.join(
        root_data_path, city_name, "norm", "trips", "my_data_source",
    )
    os.makedirs(norm_trips_data_path, exist_ok=True)

    test_booking_requests = pd.DataFrame(generate_booking_requests_list(
        od_matrices,
        week_config,
        distance_matrix,
        test_start_datetime,
        test_end_datetime,
        requests_rate_factor=1
    ))

    train_booking_requests = get_grid_indexes(grid_matrix, train_booking_requests, zone_ids)
    test_booking_requests = get_grid_indexes(grid_matrix, test_booking_requests, zone_ids)

    train_booking_requests.to_csv(os.path.join(
        norm_trips_data_path, "bookings_train.csv"
    ))
    test_booking_requests.to_csv(os.path.join(
        norm_trips_data_path, "bookings_test.csv"
    ))

    return train_booking_requests, test_booking_requests
