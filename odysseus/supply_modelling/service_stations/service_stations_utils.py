import os
import json
import geopandas as gpd
from shapely.geometry import Point


def read_stations_osm_format(city_name, grid, engine_type):

    stations_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "city_data_manager",
        "data",
        city_name,
        "raw",
        "geo",
        "openstreetmap",
        "station_locations.json"
    )
    f = open(stations_path, "r")
    station_locations = json.load(f)
    f.close()
    charging_points = station_locations[city_name][engine_type]
    points_list = []

    for point in charging_points.keys():
        points_list.append(
            {
                "geometry": Point(
                    charging_points[point]["longitude"], charging_points[point]["latitude"]
                ),
                "n_poles": charging_points[point]["n_poles"]
            }
        )
    stations_gdf = gpd.GeoDataFrame(points_list)
    n_poles_by_zone = {}
    tot_n_poles = 0
    for (p, n) in zip(stations_gdf.geometry, stations_gdf.n_poles):
        for (geom, zone) in zip(grid.geometry, grid.zone_id):
            if geom.intersects(p):
                if zone in n_poles_by_zone.keys():
                    n_poles_by_zone[zone] += n
                else:
                    n_poles_by_zone[zone] = n
                tot_n_poles += n
    return n_poles_by_zone, stations_gdf, tot_n_poles
