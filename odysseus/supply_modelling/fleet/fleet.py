import os
import json
import numpy as np


class Fleet:

    def __init__(self, grid):

        self.grid = grid
        self.n_vehicles_sim = -1
        self.vehicles_soc_dict = None
        self.vehicles_zones = None
        self.available_vehicles_dict = None

    def init_vehicles_soc(self, soc_low=25, soc_high=100):
        vehicles_random_soc = list(np.random.uniform(soc_low, soc_high, self.n_vehicles_sim).astype(int))
        self.vehicles_soc_dict = {i: vehicles_random_soc[i] for i in range(self.n_vehicles_sim)}
        return self.vehicles_soc_dict

    def init_vehicles_random_zones(self, n_initial_zones=30):
        n_initial_zones = min(n_initial_zones, len(self.grid))
        top_o_zones = self.grid.zone_id_origin_count.sort_values(ascending=False).iloc[:n_initial_zones+1]
        vehicles_random_zones = list(np.random.uniform(0, n_initial_zones, self.n_vehicles_sim).astype(int).round())
        self.vehicles_zones = []
        for i in vehicles_random_zones:
            self.vehicles_zones.append(self.grid.loc[int(top_o_zones.index[i])].zone_id)
        self.vehicles_zones = {i: self.vehicles_zones[i] for i in range(self.n_vehicles_sim)}

    def init_available_vehicles_dict(self):
        self.available_vehicles_dict = {int(zone): [] for zone in self.grid.zone_id}
        for vehicle in range(len(self.vehicles_zones)):
            zone = self.vehicles_zones[vehicle]
            self.available_vehicles_dict[zone] += [vehicle]

    def init_vehicles_from_fleet_size(self, n_vehicles_sim, how="uniform"):
        self.n_vehicles_sim = int(n_vehicles_sim)
        self.vehicles_soc_dict = self.init_vehicles_soc()
        if how == "random":
            self.init_vehicles_random_zones()
            self.init_available_vehicles_dict()
        elif how == "uniform":
            n_vehicles_per_zone = int(n_vehicles_sim / len(self.grid))
            current_zone_id = 0
            current_zone_count = 0
            self.vehicles_zones = {}
            for i in range(self.n_vehicles_sim):
                self.vehicles_zones[i] = current_zone_id
                current_zone_count += 1
                if current_zone_count >= n_vehicles_per_zone:
                    current_zone_count = 0
                    current_zone_id += 1
            self.init_available_vehicles_dict()
        self.vehicles_soc_dict = {int(k): float(v) for k, v in self.vehicles_soc_dict.items()}
        self.vehicles_zones = {int(k): int(v) for k, v in self.vehicles_zones.items()}
        self.available_vehicles_dict = {int(k): v for k, v in self.available_vehicles_dict.items()}
        return self.vehicles_soc_dict, self.vehicles_zones, self.available_vehicles_dict

    def init_vehicles_from_map_config(self, supply_model_path):
        with open(os.path.join(supply_model_path, "available_vehicles_dict.json"), "r") as f:
            self.available_vehicles_dict = json.load(f)
        with open(os.path.join(supply_model_path, "vehicles_soc_dict.json"), "r") as f:
            self.vehicles_soc_dict = json.load(f)
        with open(os.path.join(supply_model_path, "vehicles_zones.json"), "r") as f:
            self.vehicles_zones = json.load(f)
        self.n_vehicles_sim = len(self.vehicles_zones)
        return self.vehicles_soc_dict, self.vehicles_zones, self.available_vehicles_dict
