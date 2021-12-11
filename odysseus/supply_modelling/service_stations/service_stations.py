import os
import json
import numpy as np
import pandas as pd
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


class ServiceStations:

    def __init__(self, city_name, grid):

        self.city_name = city_name
        self.grid = grid

        self.tot_n_charging_poles = 0
        self.n_charging_zones = 0
        self.n_charging_poles_by_zone = None
        self.zones_cp_distances = None
        self.closest_cp_zone = None

    def get_station_distances(self):
        zones_with_cps = pd.Series(self.n_charging_poles_by_zone).index.astype(int)
        self.zones_cp_distances = self.grid.to_crs("epsg:3857").centroid.apply(
            lambda x: self.grid.loc[zones_with_cps].to_crs("epsg:3857").centroid.distance(x)
        )
        self.closest_cp_zone = self.zones_cp_distances.idxmin(axis=1)

    def init_charging_poles_from_policy(self, stations_placement_policy, engine_type):

        if stations_placement_policy == "num_parkings":

            top_dest_zones = self.grid.origin_count.sort_values(ascending=False).iloc[:self.n_charging_zones]

            self.n_charging_poles_by_zone = dict((
                top_dest_zones / top_dest_zones.sum() * self.tot_n_charging_poles
            ))

            assigned_cps = 0
            for zone_id in self.n_charging_poles_by_zone:
                zone_n_cps = int(np.floor(self.n_charging_poles_by_zone[zone_id]))
                assigned_cps += zone_n_cps
                self.n_charging_poles_by_zone[zone_id] = zone_n_cps
            for zone_id in self.n_charging_poles_by_zone:
                if assigned_cps < self.tot_n_charging_poles:
                    self.n_charging_poles_by_zone[zone_id] += 1
                    assigned_cps += 1

            self.n_charging_poles_by_zone = dict(
                pd.Series(self.n_charging_poles_by_zone).replace({0: np.NaN}).dropna()
            )

        elif stations_placement_policy in ["real_positions", "realpos_numpark"]:

            self.n_charging_poles_by_zone, self.stations_gdf, self.tot_n_charging_poles = read_stations_osm_format(
                self.city_name, self.grid, engine_type
            )
            self.n_charging_zones = len(self.n_charging_poles_by_zone.keys())

            if stations_placement_policy == "realpos_numpark":

                temp_n_charging_poles_by_zone_inf = {}

                for (p, n) in zip(self.stations_gdf.geometry, self.stations_gdf.n_poles):
                    for (geom, zone) in zip(self.grid.geometry, self.grid.zone_id):
                        if geom.intersects(p):
                            if zone in self.n_charging_poles_by_zone.keys():
                                temp_n_charging_poles_by_zone_inf[zone] += n
                            else:
                                temp_n_charging_poles_by_zone_inf[zone] = n

                top_dest_zones = self.grid.origin_count.sort_values(ascending=False).iloc[:self.n_charging_zones]
                self.n_charging_poles_by_zone = dict(
                    (top_dest_zones / top_dest_zones.sum() * self.tot_n_charging_poles)
                )
                assigned_cps = 0
                for zone_id in self.n_charging_poles_by_zone:
                    if zone_id in temp_n_charging_poles_by_zone_inf.keys():
                        zone_n_cps = int(np.floor(self.n_charging_poles_by_zone[zone_id]))
                        assigned_cps += zone_n_cps
                        self.n_charging_poles_by_zone[zone_id] = zone_n_cps
                for zone_id in self.n_charging_poles_by_zone:
                    if zone_id in temp_n_charging_poles_by_zone_inf.keys():
                        if assigned_cps < self.tot_n_charging_poles:
                            self.n_charging_poles_by_zone[zone_id] += 1
                            assigned_cps += 1

                self.n_charging_poles_by_zone = dict(
                    pd.Series(self.n_charging_poles_by_zone).replace({0: np.NaN}).dropna())

            self.n_charging_poles_by_zone = {int(k): int(v) for k, v in self.n_charging_poles_by_zone.items()}
            self.get_station_distances()

    def init_charging_poles_from_map_config(self, supply_model_path):

        with open(os.path.join(supply_model_path, "n_charging_poles_by_zone.json"), "r") as f:
            self.n_charging_poles_by_zone = json.load(f)
        self.get_station_distances()
        self.n_charging_zones = len(self.n_charging_poles_by_zone)
        for zone_id in self.n_charging_poles_by_zone:
            self.tot_n_charging_poles += self.n_charging_poles_by_zone[zone_id]
