import os
import json
import numpy as np


class Fleet:

    def __init__(self, grid, valid_zones):

        self.grid = grid
        self.valid_zones = valid_zones

        self.n_vehicles_sim = -1
        self.vehicles_soc_dict = None
        self.vehicles_zones = None
        self.available_vehicles_dict = None

    def init_vehicles_soc(self, soc_low=25, soc_high=100):
        vehicles_random_soc = list(np.random.uniform(soc_low, soc_high, self.n_vehicles_sim).astype(int))
        self.vehicles_soc_dict = {i: vehicles_random_soc[i] for i in range(self.n_vehicles_sim)}
        return self.vehicles_soc_dict

    def init_vehicles_random_greedy(self, n_initial_zones=30):
        n_initial_zones = min(n_initial_zones, len(self.grid))
        grid_origin_count = self.grid[["zone_id_origin_count"]].iloc[:, 0].fillna(0)
        top_o_zones = grid_origin_count.sort_values(ascending=False).iloc[:n_initial_zones+1]
        vehicles_random_zones = list(np.random.uniform(0, n_initial_zones, self.n_vehicles_sim).astype(int).round())
        self.vehicles_zones = []
        for i in vehicles_random_zones:
            self.vehicles_zones.append(self.grid.loc[int(top_o_zones.index[i])].zone_id)
        self.vehicles_zones = {i: self.vehicles_zones[i] for i in range(self.n_vehicles_sim)}

    def init_vehicles_random(self, n_initial_zones=30):
        vehicles_random_zones = list(np.random.uniform(0, n_initial_zones, self.n_vehicles_sim).astype(int).round())
        self.vehicles_zones = {i: vehicles_random_zones[i] for i in range(len(vehicles_random_zones))}

    def init_available_vehicles_dict(self):
        self.available_vehicles_dict = {int(zone): [] for zone in self.grid.zone_id}
        for vehicle in range(len(self.vehicles_zones)):
            zone = self.vehicles_zones[vehicle]
            self.available_vehicles_dict[zone] += [vehicle]

    def init_vehicles_from_fleet_size(self, n_vehicles_sim, how):

        self.n_vehicles_sim = int(n_vehicles_sim)
        self.vehicles_soc_dict = self.init_vehicles_soc()

        if how == "random":
            self.init_vehicles_random()

        elif how == "random_greedy":
            self.init_vehicles_random_greedy()

        elif how == "uniform":
            # TODO -> decide rule when division is not exact
            n_vehicles_per_zone = np.ceil(n_vehicles_sim / len(self.grid))
            print(n_vehicles_sim, n_vehicles_per_zone)
            current_plate = 0
            self.vehicles_zones = {}
            i = 0
            while i < n_vehicles_sim:
                for zone in self.valid_zones:
                    for i in range(current_plate, current_plate + int(n_vehicles_per_zone), 1):
                        if i >= n_vehicles_sim:
                            break
                        else:
                            self.vehicles_zones[i] = zone
                    if i >= n_vehicles_sim:
                        break
                current_plate = current_plate + int(n_vehicles_per_zone)

        self.init_available_vehicles_dict()
        self.vehicles_soc_dict = {int(k): float(v) for k, v in self.vehicles_soc_dict.items()}
        self.vehicles_zones = {int(k): int(v) for k, v in self.vehicles_zones.items()}
        self.available_vehicles_dict = {int(k): v for k, v in self.available_vehicles_dict.items()}
        return self.vehicles_soc_dict, self.vehicles_zones, self.available_vehicles_dict

    def init_from_vehicles_zones(self, vehicle_zones):
        self.vehicles_soc_dict = self.init_vehicles_soc()
        self.vehicles_zones = vehicle_zones
        self.init_available_vehicles_dict()
        return self.vehicles_soc_dict, self.vehicles_zones, self.available_vehicles_dict
