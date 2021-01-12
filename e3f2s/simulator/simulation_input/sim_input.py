import os
import pickle

import numpy as np
import pandas as pd

import datetime
import pytz

#from e3f2s.utils.vehicle_utils import get_soc_delta
from e3f2s.data_structures.vehicle import Vehicle


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
		# self.origin_scores = pickle.Unpickler(open(os.path.join(demand_model_path, "origin_scores.pickle"), "rb")).load()
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
			if "cps_zones_percentage" in self.sim_scenario_conf:
				self.n_charging_zones = int(self.sim_scenario_conf["cps_zones_percentage"] * len(self.valid_zones))
			elif "n_charging_zones" in self.sim_scenario_conf:
				self.n_charging_zones = self.sim_scenario_conf["n_charging_zones"]
				self.sim_scenario_conf["cps_zones_percentage"] = 1 / len(self.valid_zones)
			elif "cps_zones" in self.sim_scenario_conf:
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

			zones_with_cps = pd.Series(self.n_charging_poles_by_zone).index

			self.zones_cp_distances = self.grid.centroid.apply(
				lambda x: self.grid.loc[zones_with_cps].centroid.distance(x)
			)

			self.closest_cp_zone = self.zones_cp_distances.idxmin(axis=1)

	def init_relocation(self):
		if self.sim_scenario_conf["scooter_relocation"] \
				and "scooter_relocation_scheduling" in self.sim_scenario_conf.keys() \
				and self.sim_scenario_conf["scooter_relocation_scheduling"]:

			start_technique = dict(self.sim_scenario_conf["scooter_relocation_technique"])["start"]
			end_technique = dict(self.sim_scenario_conf["scooter_relocation_technique"])["end"]

			if str(start_technique).startswith("delta") or str(end_technique).startswith("delta"):
				self.origin_scores = {}
				for daytype in self.trip_kdes.keys():
					self.origin_scores[daytype] = {}
					for hour in self.trip_kdes[daytype].keys():
						self.origin_scores[daytype][hour] = self.gen_origin_scores(self.trip_kdes[daytype][hour])

	def init_workers(self):
		pass

	def gen_trip_origin_zone_from_kde(self, kde):

		def base_round(x, base):
			if x < 0:
				return 0
			elif x > base:
				return base
			else:
				return round(x)

		trip_sample = kde.sample()
		origin_i = base_round(trip_sample[0][0], len(self.grid_matrix.index) - 1)
		origin_j = base_round(trip_sample[0][1], len(self.grid_matrix.columns) - 1)

		return self.grid_matrix.loc[origin_i, origin_j]

	def gen_origin_scores(self, kde):
		origin_scores = {}
		max_iterations = len(self.available_vehicles_dict.keys()) * 100
		score_increment = 1 / max_iterations
		tot_iterations = 0
		tot_covered_density = 0
		while len(origin_scores) < len(self.available_vehicles_dict.keys()) and tot_iterations < max_iterations:
			origin_id = self.gen_trip_origin_zone_from_kde(kde)
			if origin_id in self.valid_zones:
				if origin_id in origin_scores:
					if origin_scores[origin_id] < 1:
						origin_scores[origin_id] += score_increment
						tot_covered_density += score_increment
				else:
					origin_scores[origin_id] = score_increment
					tot_covered_density += score_increment
			tot_iterations += 1
		for zone_id in self.available_vehicles_dict.keys():
			if zone_id not in origin_scores.keys():
				origin_scores[zone_id] = 0
		return origin_scores
