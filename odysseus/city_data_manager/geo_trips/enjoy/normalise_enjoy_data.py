from odysseus.city_data_manager.geo_trips.enjoy.enjoy_geo_trips import *

enjoy_geo_trips = EnjoyGeoTrips(
    "Roma", "enjoy", 2020, 10
)
enjoy_geo_trips.get_trips_od_gdfs()
enjoy_geo_trips.save_points_data()
enjoy_geo_trips.save_trips()
