import datetime
from city_data_manager.city_geo_trips.minneapolis_geo_trips import MinneapolisGeoTrips

print(datetime.datetime.now())

for month in [6, 7, 8]:
    for bin_side_length in [100, 200, 300, 400, 500]:

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
