import os
import json

from odysseus.utils.geospatial_utils import *
from odysseus.supply_modelling.service_stations.service_stations_utils import read_stations_osm_format


class ServiceStations:

    def __init__(self, city_name, grid, tot_n_charging_poles, n_charging_zones, grid_indexes_dict,
                 bin_side_length):

        self.city_name = city_name
        self.grid = grid
        self.tot_n_charging_poles = tot_n_charging_poles
        self.n_charging_zones = n_charging_zones
        self.grid_indexes_dict = grid_indexes_dict
        self.bin_side_length = bin_side_length

        self.n_charging_poles_by_zone = None
        self.zones_cp_distances = None
        self.closest_cp_zone = None

    def get_station_distances(self):

        # zones_with_cps = pd.Series(self.n_charging_poles_by_zone).index.astype(int)
        # self.zones_cp_distances = self.grid.to_crs("epsg:3857").centroid.apply(
        #     lambda x: self.grid.loc[zones_with_cps].to_crs("epsg:3857").centroid.distance(x)
        # )
        # self.closest_cp_zone = self.zones_cp_distances.idxmin(axis=1)

        self.zones_cp_distances = get_distance_matrix(
            self.grid_indexes_dict, self.grid_indexes_dict.keys(), self.n_charging_poles_by_zone.keys(),
            self.bin_side_length
        )

        self.closest_cp_zone = get_closest_zone_from_grid_matrix(
            self.grid_indexes_dict, self.grid_indexes_dict.keys(), self.n_charging_poles_by_zone.keys()
        )

    def init_charging_poles_from_policy(
            self, stations_placement_policy, engine_type
    ):

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

        elif stations_placement_policy == "uniform":
            self.n_charging_poles_by_zone = {
                zone_id: int(self.tot_n_charging_poles / self.n_charging_zones)
                for zone_id in self.grid.index.values
            }

        self.n_charging_poles_by_zone = {
            int(k): int(v) for k, v in self.n_charging_poles_by_zone.items() if v > 0
        }

        self.get_station_distances()

    def init_charging_poles_from_map_config(self, supply_model_path):

        with open(os.path.join(supply_model_path, "n_charging_poles_by_zone.json"), "r") as f:
            self.n_charging_poles_by_zone = json.load(f)
        self.get_station_distances()
        self.n_charging_zones = len(self.n_charging_poles_by_zone)
        for zone_id in self.n_charging_poles_by_zone:
            self.tot_n_charging_poles += self.n_charging_poles_by_zone[zone_id]
