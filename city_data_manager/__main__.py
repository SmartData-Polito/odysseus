import datetime
print(datetime.datetime.now())

# from city_data_manager.city_geo_trips.big_data_db_geo_trips import BigDataDBGeoTrips
#
# big_data_db_geo_trips = BigDataDBGeoTrips("Torino", "big_data_db", 2017, 10, 500)
# big_data_db_geo_trips.get_trips_od_gdfs()
# big_data_db_geo_trips.get_squared_grid()
# big_data_db_geo_trips.map_zones_on_trips(big_data_db_geo_trips.squared_grid)
# big_data_db_geo_trips.squared_grid = big_data_db_geo_trips.map_trips_on_zones(big_data_db_geo_trips.squared_grid)
# big_data_db_geo_trips.save_points_data()
# big_data_db_geo_trips.save_squared_grid()
# big_data_db_geo_trips.save_od_trips(big_data_db_geo_trips.od_trips_df, "od_trips")

from city_data_manager.city_geo_trips.minneapolis_geo_trips import MinneapolisGeoTrips

print(datetime.datetime.now())

for month in [9]:

    print(datetime.datetime.now())
    print(month)

    for bin_side_length in [200]:

        minneapolis = MinneapolisGeoTrips("city_of_minneapolis", 2019, month, bin_side_length)
        minneapolis.get_trips_od_gdfs()

        minneapolis.get_squared_grid()

        minneapolis.map_zones_on_trips(minneapolis.squared_grid)
        minneapolis.squared_grid = minneapolis.map_trips_on_zones(minneapolis.squared_grid)

        minneapolis.save_points_data()
        minneapolis.save_squared_grid()
        minneapolis.save_od_trips(minneapolis.od_trips_df, "od_trips")

        minneapolis.load()
        minneapolis.get_resampled_points_count_by_zone(
            ["zone_id"],
            "60Min"
        )
        minneapolis.save_resampled_points_data()

print(datetime.datetime.now())
