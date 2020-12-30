import os
import pickle

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import datetime
import pytz


from e3f2s.city_data_manager.data.Torino.raw.geo.openstreetmap.stations_locations import station_locations


def geodataframe_charging_points(city,engine_type,station_location):
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


class SimInput:

	def __init__(self, conf_tuple):

		self.sim_general_conf = conf_tuple[0]
		self.sim_scenario_conf = conf_tuple[1]

		self.city = self.sim_general_conf["city"]

		demand_model_path = os.path.join(
			os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
			"demand_modelling",
			"demand_models",
			self.sim_general_conf["city"],
		)

		self.grid = pickle.Unpickler(open(os.path.join(demand_model_path, "grid.pickle"), "rb")).load()
		self.grid_matrix = pickle.Unpickler(open(os.path.join(demand_model_path, "grid_matrix.pickle"), "rb")).load()
		self.request_rates = pickle.Unpickler(open(os.path.join(demand_model_path, "request_rates.pickle"), "rb")).load()
		self.trip_kdes = pickle.Unpickler(open(os.path.join(demand_model_path, "trip_kdes.pickle"), "rb")).load()
		self.valid_zones = pickle.Unpickler(open(os.path.join(demand_model_path, "valid_zones.pickle"), "rb")).load()
		self.neighbors_dict = pickle.Unpickler(open(os.path.join(demand_model_path, "neighbors_dict.pickle"), "rb")).load()
		self.integers_dict = pickle.Unpickler(open(os.path.join(demand_model_path, "integers_dict.pickle"), "rb")).load()

		self.avg_request_rate = self.integers_dict["avg_request_rate"]
		self.n_vehicles_original = self.integers_dict["n_vehicles_original"]
		self.avg_speed_mean = self.integers_dict["avg_speed_mean"]
		self.avg_speed_std = self.integers_dict["avg_speed_std"]
		self.avg_speed_kmh_mean = self.integers_dict["avg_speed_kmh_mean"]
		self.avg_speed_kmh_std = self.integers_dict["avg_speed_kmh_std"]
		self.max_driving_distance = self.integers_dict["max_driving_distance"]

		if self.sim_general_conf["sim_technique"] == "traceB":
			self.bookings = pickle.Unpickler(open(os.path.join(demand_model_path, "bookings.pickle"), "rb")).load()
			self.booking_requests_list = self.get_booking_requests_list()

		if "n_requests" in self.sim_scenario_conf.keys():
			# 30 => 1 month
			self.desired_avg_rate = self.sim_scenario_conf["n_requests"] / 30 / 24 / 3600
			self.rate_ratio = self.desired_avg_rate / self.avg_request_rate
			self.sim_scenario_conf["requests_rate_factor"] = self.rate_ratio

		if "n_vehicles" in self.sim_scenario_conf.keys():
			self.n_vehicles_sim = self.sim_scenario_conf["n_vehicles"]
		elif "n_vehicles_factor" in self.sim_scenario_conf.keys():
			self.n_vehicles_sim = int(
				self.n_vehicles_original * self.sim_scenario_conf["n_vehicles_factor"]
			)
		elif "fleet_load_factor" in self.sim_scenario_conf.keys():
			self.n_vehicles_sim = int(
				self.sim_scenario_conf["n_requests"] / self.sim_scenario_conf["fleet_load_factor"]
			)

		if "tot_n_charging_poles" in self.sim_scenario_conf.keys():
			self.tot_n_charging_poles = self.sim_scenario_conf["tot_n_charging_poles"]
		elif "n_poles_n_vehicles_factor" in self.sim_scenario_conf.keys():
			self.tot_n_charging_poles = abs(
					self.n_vehicles_sim * self.sim_scenario_conf["n_poles_n_vehicles_factor"]
			)
		elif self.sim_scenario_conf["cps_placement_policy"] == "old_manual":
			self.tot_n_charging_poles = len(self.sim_scenario_conf["cps_zones"]) * 4

		if self.sim_scenario_conf["distributed_cps"]:
			if "cps_zones_percentage" in self.sim_scenario_conf and self.sim_scenario_conf["cps_placement_policy"] != "real_positions":
				self.n_charging_zones = int(self.sim_scenario_conf["cps_zones_percentage"] * len(self.valid_zones))
			elif "n_charging_zones" in self.sim_scenario_conf and self.sim_scenario_conf["cps_placement_policy"] != "real_positions":
				self.n_charging_zones = self.sim_scenario_conf["n_charging_zones"]
				self.sim_scenario_conf["cps_zones_percentage"] = 1 / len(self.valid_zones)
			elif "cps_zones" in self.sim_scenario_conf and self.sim_scenario_conf["cps_placement_policy"] != "real_positions":
				self.n_charging_zones = len(self.sim_scenario_conf["cps_zones"])
		elif self.sim_scenario_conf["battery_swap"]:
			self.n_charging_zones = 0
			self.tot_n_charging_poles = 0

		self.n_charging_poles_by_zone = {}
		self.vehicles_soc_dict = {}
		self.vehicles_zones = {}
		self.available_vehicles_dict = {}

		self.start = None

		self.zones_cp_distances = pd.Series()
		self.closest_cp_zone = pd.Series()

	def get_booking_requests_list(self):

		return self.bookings[[
			"origin_id",
			"destination_id",
			"start_time",
			"end_time",
			"ia_timeout",
			"euclidean_distance",
			"driving_distance",
			"date",
			"hour",
			"duration"
		]].dropna().to_dict("records")
		return

	def init_vehicles(self):

		vehicles_random_soc = list(
			np.random.uniform(25, 100, self.n_vehicles_sim).astype(int)
		)

		self.vehicles_soc_dict = {
			i: vehicles_random_soc[i] for i in range(self.n_vehicles_sim)
		}

		top_o_zones = self.grid.origin_count.sort_values(ascending=False).iloc[:31]

		vehicles_random_zones = list(
			np.random.uniform(0, 30, self.n_vehicles_sim).astype(int).round()
		)

		self.vehicles_zones = []
		for i in vehicles_random_zones:
			self.vehicles_zones.append(self.grid.loc[int(top_o_zones.index[i])].zone_id)

		self.vehicles_zones = {
			i: self.vehicles_zones[i] for i in range(self.n_vehicles_sim)
		}

		self.available_vehicles_dict = {
			int(zone): [] for zone in self.grid.zone_id
		}

		for vehicle in range(len(self.vehicles_zones)):
			zone = self.vehicles_zones[vehicle]
			self.available_vehicles_dict[zone] += [vehicle]

		self.start = datetime.datetime(
			self.sim_general_conf["year"],
			self.sim_general_conf["month_start"],
			1, tzinfo=pytz.UTC
		)

		return self.vehicles_soc_dict, self.vehicles_zones, self.available_vehicles_dict

	def init_charging_poles(self):

		if self.sim_scenario_conf["distributed_cps"]:

			if self.sim_scenario_conf["cps_placement_policy"] == "num_parkings":

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

			elif self.sim_scenario_conf["cps_placement_policy"] == "old_manual":

				for zone_id in self.sim_scenario_conf["cps_zones"]:
					if zone_id in self.valid_zones:
						self.n_charging_poles_by_zone[zone_id] = 4
					else:
						print("Zone", zone_id, "does not exist!")
						exit(0)

			elif self.sim_scenario_conf["cps_placement_policy"] == "real_positions":
				cps_points = geodataframe_charging_points(
					self.city, self.sim_scenario_conf["engine_type"], station_locations
				)
				self.n_charging_poles_by_zone = {}
				value = 0
				for (p,n) in zip(cps_points.geometry,cps_points.n_poles):
					for (geom,zone) in zip(self.grid.geometry,self.grid.zone_id):
						if geom.intersects(p) == True:
							if zone in self.n_charging_poles_by_zone.keys():
								self.n_charging_poles_by_zone[zone] += n
							else:
								self.n_charging_poles_by_zone[zone] = n
							value += n
				self.tot_n_charging_poles = value
				self.n_charging_zones = len(self.n_charging_poles_by_zone.keys())

			zones_with_cps = pd.Series(self.n_charging_poles_by_zone).index

			self.zones_cp_distances = self.grid.centroid.apply(
				lambda x: self.grid.loc[zones_with_cps].centroid.distance(x)
			)

			self.closest_cp_zone = self.zones_cp_distances.idxmin(axis=1)

	def init_relocation(self):
		pass

	def init_workers(self):
		pass
