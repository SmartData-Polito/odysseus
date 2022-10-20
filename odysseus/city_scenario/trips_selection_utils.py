def filter_trips_v1(bookings, city_name, data_source_id):

    if city_name in [
        "Minneapolis", "Louisville", "Austin", "Norfolk", "Kansas City", "Chicago", "Calgary"
    ] or data_source_id in ["citi_bike"]:
        bookings = bookings[bookings.avg_speed_kmh < 30]
        bookings = bookings[
            (bookings.duration > 60) & (
                    bookings.duration < 60 * 60
            ) & (bookings.euclidean_distance > 200)
        ]

    elif data_source_id in ["big_data_db"]:
        bookings = bookings[bookings.avg_speed_kmh < 120]
        bookings = bookings[
            (bookings.duration > 3 * 60) & (
                    bookings.duration < 60 * 60
            ) & (bookings.euclidean_distance > 500)
        ]
    return bookings
