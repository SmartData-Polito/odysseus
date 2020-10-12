import datetime
print(datetime.datetime.now())

from e3f2s.city_data_manager.city_geo_trips.big_data_db_geo_trips import BigDataDBGeoTrips

for month in [10]:
    big_data_db_geo_trips = BigDataDBGeoTrips("Torino", "big_data_db", 2017, month)
    big_data_db_geo_trips.get_trips_od_gdfs()
    big_data_db_geo_trips.save_points_data()
    big_data_db_geo_trips.save_trips()

# from e3f2s.city_data_manager.city_geo_trips.minneapolis_geo_trips import MinneapolisGeoTrips
#
# print(datetime.datetime.now())
#
# for month in [7]:
#
#     print(datetime.datetime.now())
#
#     for bin_side_length in [200]:
#
#         minneapolis = MinneapolisGeoTrips("city_of_minneapolis", 2019, month, bin_side_length)
#         minneapolis.get_trips_od_gdfs()
#
#         minneapolis.get_squared_grid()
#
#         minneapolis.map_zones_on_trips(minneapolis.squared_grid)
#         minneapolis.squared_grid = minneapolis.map_trips_on_zones(minneapolis.squared_grid)
#
#         minneapolis.save_points_data()
#         minneapolis.save_squared_grid()
#         minneapolis.save_od_trips(minneapolis.od_trips_df, "od_trips")
#
#         minneapolis.load()
#         # minneapolis.get_resampled_points_count_by_zone(
#         #     ["zone_id"],
#         #     "60Min"
#         # )
#         # minneapolis.save_resampled_points_data()
#
# print(datetime.datetime.now())

# from e3f2s.city_data_manager.city_geo_trips.louisville_geo_trips import LouisvilleGeoTrips
#
# print(datetime.datetime.now())
#
# for month in [7, 8, 9]:
#
#     print(datetime.datetime.now())
#     print(month)
#
#     for bin_side_length in [200]:
#
#         louisville = LouisvilleGeoTrips("city_of_louisville", 2019, month, bin_side_length)
#         louisville.get_trips_od_gdfs()
#
#         louisville.get_squared_grid()
#
#         louisville.map_zones_on_trips(louisville.squared_grid)
#         louisville.squared_grid = louisville.map_trips_on_zones(louisville.squared_grid)
#
#         louisville.save_points_data()
#         louisville.save_squared_grid()
#         louisville.save_od_trips(louisville.od_trips_df, "od_trips")
#
#         louisville.load()
#         louisville.get_resampled_points_count_by_zone(
#             ["zone_id"],
#             "60Min"
#         )
#         louisville.save_resampled_points_data()

print(datetime.datetime.now())
