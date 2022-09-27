from odysseus.city_data_manager.od_matrices.od_generator import *


def generate_booking_requests_list(
        od_matrices, start_datetime, end_datetime
):
    booking_requests_list = list()
    current_datetime = start_datetime
    print(current_datetime)
    current_hour = current_datetime.hour
    current_weekday = current_datetime.weekday()
    current_daytype = get_daytype_from_weekday(current_weekday)
    seconds_spent = 0
    while current_datetime < end_datetime:
        for o_id in od_matrices[current_daytype][current_hour].index:
            for d_id in od_matrices[current_daytype][current_hour].columns:
                n_bookings_to_generate = int(od_matrices[current_daytype][current_hour].loc[o_id, d_id])
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
                        booking_request["origin_i"] = od_matrices[current_daytype][current_hour]
                        cum_timeout += timeout_sec
                        booking_requests_list.append(booking_request)
                        seconds_spent += timeout_sec
        current_datetime += datetime.timedelta(seconds=3600)
        current_hour = current_datetime.hour
        current_weekday = current_datetime.weekday()
        current_daytype = get_daytype_from_weekday(current_weekday)

    return booking_requests_list


def generate_trips_from_od(
        city_name, od_matrices, grid_matrix, zone_ids,
        train_start_datetime, train_end_datetime, test_start_datetime, test_end_datetime
):
    train_booking_requests = pd.DataFrame(generate_booking_requests_list(
        od_matrices,
        train_start_datetime,
        train_end_datetime,
    ))
    norm_trips_data_path = os.path.join(
        root_data_path, city_name, "norm", "trips", "my_data_source",
    )
    os.makedirs(norm_trips_data_path, exist_ok=True)

    test_booking_requests = pd.DataFrame(generate_booking_requests_list(
        od_matrices,
        test_start_datetime,
        test_end_datetime,
    ))

    train_booking_requests = get_grid_indexes(grid_matrix, train_booking_requests, zone_ids)
    test_booking_requests = get_grid_indexes(grid_matrix, test_booking_requests, zone_ids)

    train_booking_requests.to_csv(os.path.join(
        norm_trips_data_path, "bookings_train.csv"
    ))
    test_booking_requests.to_csv(os.path.join(
        norm_trips_data_path, "bookings_test.csv"
    ))
