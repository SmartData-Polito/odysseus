import os
import pickle
import json
import numpy as np
import pandas as pd


from odysseus.supply_modelling.fleet.fleet import Fleet
from odysseus.supply_modelling.fleet.vehicle_conf import vehicle_conf as standard_vehicle_configs

from odysseus.supply_modelling.service_stations.service_stations import ServiceStations

from odysseus.simulator.simulation_data_structures.zone import Zone
from odysseus.simulator.simulation_data_structures.vehicle import Vehicle
from odysseus.simulator.simulation_data_structures.charging_station import ChargingStation

from odysseus.city_scenario.city_scenario_from_wgs84_trips import CityScenarioFromTrips

from odysseus.city_scenario.energy_mix_loader import EnergyMix


class SupplyModel:

    def __init__(
            self,
            city_name, data_source_id,
            city_scenario_folder, supply_model_folder,
            supply_model_conf
    ):

        self.city_name = city_name
        self.data_source_id = data_source_id
        self.city_scenario_folder = city_scenario_folder
        self.supply_model_folder = supply_model_folder
        self.supply_model_conf = supply_model_conf

        self.supply_model_path = None

        self.city_scenario = CityScenarioFromTrips(
            city_name=self.city_name,
            data_source_id=self.data_source_id,
            read_config_from_file=True,
            in_folder_name=self.city_scenario_folder
        )
        self.city_scenario.read_city_scenario_for_supply_model()

        self.tot_n_charging_poles = 0
        self.n_charging_zones = 0
        self.n_vehicles_sim = 0
        self.real_n_charging_zones = 0

        self.grid = self.city_scenario.grid
        self.grid = self.grid.loc[:, ~self.grid.columns.duplicated()]
        self.valid_zones = self.city_scenario.valid_zones
        self.neighbors_dict = self.city_scenario.neighbors_dict
        self.numerical_params_dict = self.city_scenario.numerical_params_dict
        self.avg_speed_mean = self.numerical_params_dict["avg_speed_mean"]
        self.avg_speed_std = self.numerical_params_dict["avg_speed_std"]
        self.max_driving_distance = self.numerical_params_dict["max_driving_distance"]
        self.year_energy_mix = int(self.numerical_params_dict["year_energy_mix"])

        self.n_charging_poles_by_zone = {}
        self.vehicles_soc_dict = {}
        self.vehicles_zones = {}
        self.available_vehicles_dict = {}

        self.zones_cp_distances = pd.Series(dtype=float)
        self.closest_cp_zone = pd.Series(dtype=float)
        self.energy_mix = EnergyMix(self.city_name, self.year_energy_mix)

        self.initial_relocation_workers_positions = []

        self.service_stations = None
        self.zone_dict = dict()
        self.charging_stations_dict = dict()

        self.fleet = Fleet(self.grid, self.valid_zones)
        self.vehicles_list = list()

        self.simpy_env = None

    def init_vehicles(self):

        if self.supply_model_conf["vehicles_config_mode"] == "sim_config":

            self.n_vehicles_sim = int(self.supply_model_conf["n_vehicles"])
            # self.tot_n_charging_poles = int(self.supply_model_conf["tot_n_charging_poles"])
            # self.n_charging_zones = int(self.supply_model_conf["n_charging_zones"])

            self.vehicles_soc_dict, self.vehicles_zones, self.available_vehicles_dict = \
                self.fleet.init_vehicles_from_fleet_size(
                    self.n_vehicles_sim,
                    self.supply_model_conf["vehicles_initial_placement"]
                )

        elif self.supply_model_conf["vehicles_config_mode"] == "vehicles_zones":

            vehicles_zones = dict(self.supply_model_conf["vehicles_zones"])
            self.n_vehicles_sim = len(self.supply_model_conf["vehicles_zones"])
            self.fleet.n_vehicles_sim = self.n_vehicles_sim
            self.vehicles_soc_dict, self.vehicles_zones, self.available_vehicles_dict = \
                self.fleet.init_from_vehicles_zones(vehicles_zones)

        return self.vehicles_soc_dict, self.vehicles_zones, self.available_vehicles_dict

    def init_supply_model_path(self):

        assert self.supply_model_folder
        self.supply_model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "supply_modelling",
            "city_supply_models",
            self.city_name,
            self.supply_model_folder
        )

    def init_charging_poles(self):

        if self.supply_model_conf["distributed_cps"]:

            if self.supply_model_conf["stations_placement_config_mode"] == "sim_config":

                assert "n_charging_zones" in self.supply_model_conf.keys()
                self.n_charging_zones = self.supply_model_conf["n_charging_zones"]
                self.tot_n_charging_poles = self.supply_model_conf["tot_n_charging_poles"]

                self.service_stations = ServiceStations(
                    self.city_name, self.grid, self.tot_n_charging_poles, self.n_charging_zones,
                    self.city_scenario.grid_indexes_dict, self.city_scenario.bin_side_length
                )

                self.service_stations.init_charging_poles_from_policy(
                    self.supply_model_conf["cps_placement_policy"],
                    self.supply_model_conf["engine_type"],
                )

            elif self.supply_model_conf["stations_placement_config_mode"] == "n_charging_poles_by_zone":

                self.service_stations = ServiceStations(
                    self.city_name, self.grid, 0, 0,
                    self.city_scenario.grid_indexes_dict, self.city_scenario.bin_side_length
                )
                self.service_stations.init_charging_poles_from_map_config(
                    dict(self.supply_model_conf["n_charging_poles_by_zone"])
                )

            self.n_charging_poles_by_zone = self.service_stations.n_charging_poles_by_zone
            self.zones_cp_distances = self.service_stations.zones_cp_distances
            self.closest_cp_zone = self.service_stations.closest_cp_zone

    def init_relocation(self, n_initial_zones=30):

        n_initial_zones = min(n_initial_zones, len(self.grid))

        if "n_relocation_workers" in self.supply_model_conf:

            n_relocation_workers = self.supply_model_conf["n_relocation_workers"]

            top_o_zones = self.grid.zone_id_origin_count.sort_values(ascending=False).iloc[:31]

            workers_random_zones = list(
                np.random.uniform(0, n_initial_zones, n_relocation_workers).astype(int).round()
            )

            self.initial_relocation_workers_positions = [
                int(self.grid.loc[int(top_o_zones.index[i])].zone_id) for i in workers_random_zones
            ]

    def save_results(self):

        self.init_supply_model_path()

        os.makedirs(self.supply_model_path, exist_ok=True)

        with open(os.path.join(self.supply_model_path, "supply_model.pickle"), "wb") as f:
            pickle.dump(self, f)

        with open(os.path.join(self.supply_model_path, "supply_model_conf.json"), "w") as f:
            json.dump(self.supply_model_conf, f, sort_keys=True, indent=4)
        with open(os.path.join(self.supply_model_path, "n_charging_poles_by_zone.json"), "w") as f:
            json.dump(self.n_charging_poles_by_zone, f, sort_keys=True, indent=4)
        with open(os.path.join(self.supply_model_path, "vehicles_soc_dict.json"), "w") as f:
            json.dump(self.vehicles_soc_dict, f, sort_keys=True, indent=4)
        with open(os.path.join(self.supply_model_path, "vehicles_zones.json"), "w") as f:
            json.dump(self.vehicles_zones, f, sort_keys=True, indent=4)
        with open(os.path.join(self.supply_model_path, "available_vehicles_dict.json"), "w") as f:
            json.dump(self.available_vehicles_dict, f, sort_keys=True, indent=4)
        with open(os.path.join(self.supply_model_path, "initial_relocation_workers_positions.json"), "w") as f:
            json.dump(self.initial_relocation_workers_positions, f, sort_keys=True, indent=4)

    def init_for_simulation(
            self, simpy_env, start, station_conf, vehicle_conf,
    ):

        self.simpy_env = simpy_env

        for zone_id in self.valid_zones:
            self.zone_dict[zone_id] = Zone(self.simpy_env, zone_id, start, self.available_vehicles_dict[zone_id])

        if self.supply_model_conf["distributed_cps"]:

            for zone_id in self.n_charging_poles_by_zone:

                zone_n_cps = self.n_charging_poles_by_zone[zone_id]
                if zone_n_cps > 0:
                    self.charging_stations_dict[zone_id] = ChargingStation(
                        self.simpy_env, zone_n_cps, zone_id, station_conf,
                        vehicle_conf["engine_type"],
                        self.supply_model_conf["profile_type"],
                        start
                    )
                    self.real_n_charging_zones += zone_n_cps

        for i in range(self.n_vehicles_sim):

            if self.supply_model_conf["profile_type"] == "fixed_duration":
                vehicle_conf["fixed_charging_duration"] = self.supply_model_conf["fixed_charging_duration"]

            if self.supply_model_conf["engine_type"] == "electric":
                vehicle_conf["max_charg_power"] = standard_vehicle_configs["electric"][
                    vehicle_conf["vehicle_model_name"]
                ]["max_charg_power"]

            vehicle_object = Vehicle(
                self.simpy_env, i, self.vehicles_zones[i], self.vehicles_soc_dict[i],
                vehicle_conf, self.energy_mix, start
            )
            self.vehicles_list.append(vehicle_object)

        if "alpha_policy" in self.supply_model_conf:
            if self.supply_model_conf["alpha_policy"] == "auto":
                self.supply_model_conf["alpha"] = self.vehicles_list[0].consumption_to_percentage(
                    self.vehicles_list[0].distance_to_consumption(
                        self.max_driving_distance / 1000
                    )
                )
            elif self.supply_model_conf["alpha_policy"] == "sim_config":
                assert "alpha" in self.supply_model_conf
        else:
            print("Policy for alpha not recognised!")
            exit(0)
