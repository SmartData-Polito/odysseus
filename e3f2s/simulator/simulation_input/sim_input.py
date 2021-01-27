import os
import pickle

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


import datetime
import pytz

#from e3f2s.utils.vehicle_utils import get_soc_delta
#from e3f2s.data_structures.vehicle import Vehicle


class SimInput:

	def __init__(self, conf_tuple):

		self.sim_general_conf = conf_tuple[0]
		self.sim_scenario_conf = conf_tuple[1]
		self.city_obj = conf_tuple[2]

		self.city = self.city_obj.city_name
		self.grid = self.city_obj.grid
		self.grid_matrix = self.city_obj.grid_matrix
		self.input_bookings = self.city_obj.bookings
		print(self.input_bookings.shape)
		self.request_rates = self.city_obj.request_rates
		self.avg_request_rate = self.city_obj.avg_request_rate
		self.trip_kdes = self.city_obj.trip_kdes
		self.valid_zones = self.city_obj.valid_zones
		self.neighbors_dict = self.city_obj.neighbors_dict
		self.n_vehicles_original = self.city_obj.n_vehicles_original

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

		self.hub_zone = -1

		if self.sim_scenario_conf["hub"]:
			self.n_charging_zones = 1
			self.sim_scenario_conf["cps_zones_percentage"] = 1 / len(self.valid_zones)
		elif self.sim_scenario_conf["distributed_cps"]:
			if "cps_zones_percentage" in self.sim_scenario_conf:
				self.n_charging_zones = int(self.sim_scenario_conf["cps_zones_percentage"] * len(self.valid_zones))
			elif "n_charging_zones" in self.sim_scenario_conf:
				self.n_charging_zones = self.sim_scenario_conf["n_charging_zones"]
				self.sim_scenario_conf["cps_zones_percentage"] = 1 / len(self.valid_zones)
			elif "cps_zones" in self.sim_scenario_conf:
				self.n_charging_zones = len(self.sim_scenario_conf["cps_zones"])
		elif self.sim_scenario_conf["battery_swap"]:
			self.n_charging_zones = 0

		if self.sim_scenario_conf["hub"] and not self.sim_scenario_conf["distributed_cps"]:
			self.hub_n_charging_poles = int(self.tot_n_charging_poles)
			self.n_charging_poles = 0
		elif not self.sim_scenario_conf["hub"] and self.sim_scenario_conf["distributed_cps"]:
			self.hub_n_charging_poles = 0
			self.n_charging_poles = self.tot_n_charging_poles
		elif self.sim_scenario_conf["hub"] and self.sim_scenario_conf["distributed_cps"]:
			self.n_charging_poles = int(self.tot_n_charging_poles / 2)
			self.hub_n_charging_poles = int(self.tot_n_charging_poles / 2)
		elif self.sim_scenario_conf["battery_swap"]:
			self.n_charging_poles = 0



		self.avg_speed_mean = self.input_bookings.avg_speed.mean()
		self.avg_speed_std = self.input_bookings.avg_speed.std()
		self.avg_speed_kmh_mean = self.input_bookings.avg_speed_kmh.mean()
		self.avg_speed_kmh_std = self.input_bookings.avg_speed_kmh.std()

		self.n_charging_poles_by_zone = {}
		self.booking_requests_list = []
		self.vehicles_soc_dict = {}
		self.vehicles_zones = {}
		self.available_vehicles_dict = {}

		self.start = None

		self.zones_cp_distances = pd.Series()
		self.closest_cp_zone = pd.Series()

	def get_booking_requests_list(self):

		self.booking_requests_list = self.input_bookings[[
			"origin_id",
			"destination_id",
			"start_time",
			"end_time",
			"ia_timeout",
			"euclidean_distance",
			"driving_distance",
			"date",
			"hour",
			"duration",
		]].dropna().to_dict("records")
		return self.booking_requests_list

	def init_vehicles(self):
		return self.supply_model.init_vehicles()

	def init_charging_poles(self):

		if self.sim_scenario_conf["distributed_cps"]:

			if self.sim_scenario_conf["cps_placement_policy"] == "num_parkings":

				top_dest_zones = self.input_bookings.destination_id.value_counts().iloc[:self.n_charging_zones]

				self.n_charging_poles_by_zone = dict((top_dest_zones / top_dest_zones.sum() * self.n_charging_poles))

				assigned_cps = 0
				for zone_id in self.n_charging_poles_by_zone:
					zone_n_cps = int(np.floor(self.n_charging_poles_by_zone[zone_id]))
					assigned_cps += zone_n_cps
					self.n_charging_poles_by_zone[zone_id] = zone_n_cps
				for zone_id in self.n_charging_poles_by_zone:
					if assigned_cps < self.n_charging_poles:
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
		pass

	def init_workers(self):
		pass
