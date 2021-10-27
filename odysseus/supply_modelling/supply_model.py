import os
import pickle
import json
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import datetime
import pytz
from odysseus.supply_modelling.energymix_loader import EnergyMix

from odysseus.city_scenario.city_scenario import CityScenario


def geodataframe_charging_points(city, engine_type, station_location):
    charging_points = station_location[city][engine_type]
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
    return gpd.GeoDataFrame(points_list)


class SupplyModel:

    def __init__(self, supply_model_conf):

        self.supply_model_conf = supply_model_conf

        self.city_name = self.supply_model_conf["city"]
        self.city_scenario_folder = self.supply_model_conf["city_scenario_folder"]
        self.supply_model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "supply_modelling",
            "supply_models",
            self.city_name,
            self.city_scenario_folder
        )

        self.city_scenario = CityScenario(
            city=self.city_name,
            from_file=True,
            in_folder_name=self.city_scenario_folder
        )
        self.city_scenario.read_city_scenario_for_supply_model()

        self.grid = self.city_scenario.grid
        self.valid_zones = self.city_scenario.valid_zones
        self.neighbors_dict = self.city_scenario.neighbors_dict
        self.integers_dict = self.city_scenario.integers_dict
        self.avg_speed_mean = self.integers_dict["avg_speed_mean"]
        self.avg_speed_std = self.integers_dict["avg_speed_std"]

        self.n_vehicles_sim = int(self.supply_model_conf["n_vehicles"])
        self.tot_n_charging_poles = int(self.supply_model_conf["tot_n_charging_poles"])
        self.n_charging_zones = int(self.supply_model_conf["n_charging_zones"])

        self.n_charging_poles_by_zone = {}
        self.vehicles_soc_dict = {}
        self.vehicles_zones = {}
        self.available_vehicles_dict = {}

        self.zones_cp_distances = pd.Series()
        self.closest_cp_zone = pd.Series()
        self.energy_mix = self.city_scenario.energy_mix

        self.initial_relocation_workers_positions = []

    def init_vehicles(self):

        vehicles_random_soc = list(np.random.uniform(25, 100, self.n_vehicles_sim).astype(int))
        self.vehicles_soc_dict = {i: vehicles_random_soc[i] for i in range(self.n_vehicles_sim)}
        top_o_zones = self.grid.zone_id_origin_count.sort_values(ascending=False).iloc[:31]
        vehicles_random_zones = list(np.random.uniform(0, 30, self.n_vehicles_sim).astype(int).round())
        self.vehicles_zones = []
        for i in vehicles_random_zones:
            self.vehicles_zones.append(self.grid.loc[int(top_o_zones.index[i])].zone_id)
        self.vehicles_zones = {i: self.vehicles_zones[i] for i in range(self.n_vehicles_sim)}
        self.available_vehicles_dict = {int(zone): [] for zone in self.grid.zone_id}
        for vehicle in range(len(self.vehicles_zones)):
            zone = self.vehicles_zones[vehicle]
            self.available_vehicles_dict[zone] += [vehicle]

        self.vehicles_soc_dict = {int(k): float(v) for k, v in self.vehicles_soc_dict.items()}
        self.vehicles_zones = {int(k): int(v) for k, v in self.vehicles_zones.items()}
        self.available_vehicles_dict = {int(k): v for k, v in self.available_vehicles_dict.items()}

        return self.vehicles_soc_dict, self.vehicles_zones, self.available_vehicles_dict

    def init_charging_poles(self):

        if self.supply_model_conf["distributed_cps"]:

            if self.supply_model_conf["cps_placement_policy"] == "num_parkings":

                top_dest_zones = self.grid.origin_count.sort_values(ascending=False).iloc[:self.n_charging_zones]

                self.n_charging_poles_by_zone = dict((top_dest_zones / top_dest_zones.sum() * self.tot_n_charging_poles))

                assigned_cps = 0
                for zone_id in self.n_charging_poles_by_zone:
                    zone_n_cps = int(np.floor(self.n_charging_poles_by_zone[zone_id]))
                    assigned_cps += zone_n_cps
                    self.n_charging_poles_by_zone[zone_id] = zone_n_cps
                for zone_id in self.n_charging_poles_by_zone:
                    if assigned_cps < self.tot_n_charging_poles:
                        self.n_charging_poles_by_zone[zone_id] += 1
                        assigned_cps += 1

                self.n_charging_poles_by_zone = dict(pd.Series(self.n_charging_poles_by_zone).replace({0: np.NaN}).dropna())

            elif self.supply_model_conf["cps_placement_policy"] == "old_manual":

                for zone_id in self.supply_model_conf["cps_zones"]:
                    if zone_id in self.valid_zones:
                        self.n_charging_poles_by_zone[zone_id] = 4
                    else:
                        print("Zone", zone_id, "does not exist!")
                        exit(0)

            elif self.supply_model_conf["cps_placement_policy"] == "real_positions":
                stations_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "city_data_manager",
                    "data",
                    self.supply_model_conf["city"],
                    "raw",
                    "geo",
                    "openstreetmap",
                    "station_locations.json"
                )
                f = open(stations_path,"r")
                station_locations = json.load(f)
                f.close()
                cps_points = geodataframe_charging_points(
                    self.city_name, self.supply_model_conf["engine_type"], station_locations
                )
                self.n_charging_poles_by_zone = {}
                value = 0
                for (p,n) in zip(cps_points.geometry,cps_points.n_poles):
                    for (geom,zone) in zip(self.grid.geometry,self.grid.zone_id):
                        if geom.intersects(p):
                            if zone in self.n_charging_poles_by_zone.keys():
                                self.n_charging_poles_by_zone[zone] += n
                            else:
                                self.n_charging_poles_by_zone[zone] = n
                            value += n
                self.tot_n_charging_poles = value
                self.n_charging_zones = len(self.n_charging_poles_by_zone.keys())

            elif self.supply_model_conf["cps_placement_policy"] == "realpos_numpark":
                stations_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "city_data_manager",
                    "data",
                    self.supply_model_conf["city"],
                    "raw",
                    "geo",
                    "openstreetmap",
                    "station_locations.json"
                )
                f = open(stations_path, "r")
                station_locations = json.load(f)
                f.close()
                cps_points = geodataframe_charging_points(
                    self.city_name, self.supply_model_conf["engine_type"], station_locations
                )
                self.n_charging_poles_by_zone_inf = {}

                for (p, n) in zip(cps_points.geometry, cps_points.n_poles):
                    for (geom, zone) in zip(self.grid.geometry, self.grid.zone_id):
                        if geom.intersects(p):
                            if zone in self.n_charging_poles_by_zone.keys():
                                self.n_charging_poles_by_zone_inf[zone] += n
                            else:
                                self.n_charging_poles_by_zone_inf[zone] = n

                top_dest_zones = self.grid.origin_count.sort_values(ascending=False).iloc[:self.n_charging_zones]
                self.n_charging_poles_by_zone = dict(
                    (top_dest_zones / top_dest_zones.sum() * self.tot_n_charging_poles))
                assigned_cps = 0
                for zone_id in self.n_charging_poles_by_zone:
                    if zone_id in self.n_charging_poles_by_zone_inf.keys():
                        zone_n_cps = int(np.floor(self.n_charging_poles_by_zone[zone_id]))
                        assigned_cps += zone_n_cps
                        self.n_charging_poles_by_zone[zone_id] = zone_n_cps
                for zone_id in self.n_charging_poles_by_zone:
                    if zone_id in self.n_charging_poles_by_zone_inf.keys():
                        if assigned_cps < self.tot_n_charging_poles:
                            self.n_charging_poles_by_zone[zone_id] += 1
                            assigned_cps += 1

                self.n_charging_poles_by_zone = dict(
                    pd.Series(self.n_charging_poles_by_zone).replace({0: np.NaN}).dropna())

            self.n_charging_poles_by_zone = {int(k): int(v) for k, v in self.n_charging_poles_by_zone.items()}
            zones_with_cps = pd.Series(self.n_charging_poles_by_zone).index
            self.zones_cp_distances = self.grid.to_crs("epsg:3857").centroid.apply(
                lambda x: self.grid.loc[zones_with_cps].to_crs("epsg:3857").centroid.distance(x)
            )
            self.closest_cp_zone = self.zones_cp_distances.idxmin(axis=1)

    def init_relocation(self):

        if "n_relocation_workers" in self.supply_model_conf:

            n_relocation_workers = self.supply_model_conf["n_relocation_workers"]

            top_o_zones = self.grid.zone_id_origin_count.sort_values(ascending=False).iloc[:31]

            workers_random_zones = list(
                np.random.uniform(0, 30, n_relocation_workers).astype(int).round()
            )

            self.initial_relocation_workers_positions = [
                int(self.grid.loc[int(top_o_zones.index[i])].zone_id) for i in workers_random_zones
            ]

    def save_results(self):

        os.makedirs(self.supply_model_path, exist_ok=True)

        with open(os.path.join(self.supply_model_path, "supply_model.pickle"), "wb") as f:
            pickle.dump(self, f)

        with open(os.path.join(self.supply_model_path, "n_charging_poles_by_zone.json"), "w") as f:
            json.dump(self.n_charging_poles_by_zone, f, sort_keys=True, indent=4)
        with open(os.path.join(self.supply_model_path, "vehicles_soc_dict.json"), "w") as f:
            json.dump(self.vehicles_soc_dict, f)
        with open(os.path.join(self.supply_model_path, "vehicles_zones.json"), "w") as f:
            json.dump(self.vehicles_zones, f)
        with open(os.path.join(self.supply_model_path, "available_vehicles_dict.json"), "w") as f:
            json.dump(self.available_vehicles_dict, f)
        with open(os.path.join(self.supply_model_path, "initial_relocation_workers_positions.json"), "w") as f:
            json.dump(self.initial_relocation_workers_positions, f)
