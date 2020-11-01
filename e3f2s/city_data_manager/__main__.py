import datetime


from e3f2s.city_data_manager.city_geo_trips.big_data_db_geo_trips import BigDataDBGeoTrips

for month in [10]:

    print(datetime.datetime.now(), "Turin", month)

    big_data_db_geo_trips = BigDataDBGeoTrips("Torino", "big_data_db", 2017, month)
    big_data_db_geo_trips.get_trips_od_gdfs()
    big_data_db_geo_trips.save_points_data()
    big_data_db_geo_trips.save_trips()


from e3f2s.city_data_manager.city_geo_trips.minneapolis_geo_trips import MinneapolisGeoTrips

for month in [7]:

    print(datetime.datetime.now(), "Minneapolis", month)

    minneapolis = MinneapolisGeoTrips("city_of_minneapolis", 2019, month)
    minneapolis.get_trips_od_gdfs()
    minneapolis.save_points_data()
    minneapolis.save_trips()


from e3f2s.city_data_manager.city_geo_trips.louisville_geo_trips import LouisvilleGeoTrips

for month in [7, 8, 9]:

    print(datetime.datetime.now(), "Louisville", month)

    louisville = LouisvilleGeoTrips("city_of_louisville", 2019, month)
    louisville.get_trips_od_gdfs()
    louisville.save_points_data()
    louisville.save_trips()

print(datetime.datetime.now(), "Done")
