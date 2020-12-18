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

		vehicles_random_soc = list(
			np.random.uniform(25, 100, self.n_vehicles_sim).astype(int)
		)

		self.vehicles_soc_dict = {
			i: vehicles_random_soc[i] for i in range(self.n_vehicles_sim)
		}

		top_o_zones = self.input_bookings.origin_id.value_counts().iloc[:31]

		print(len(self.valid_zones), len(self.grid), len(top_o_zones.index))

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

	def init_hub(self):

		if self.sim_scenario_conf["hub"]:
			if self.sim_scenario_conf["hub_zone_policy"] == "manual":

				if self.sim_scenario_conf["hub_zone"] in self.valid_zones:
					self.hub_zone = self.sim_scenario_conf["hub_zone"]
				else:
					print("Hub zone does not exist!")
					exit(1)

			elif self.sim_scenario_conf["hub_zone_policy"] == "num_parkings":
				self.hub_zone = int(self.input_bookings.destination_id.value_counts().iloc[:1].index[0])

			else:
				print("Hub placement policy not recognised!")
				exit(0)

			for zone in self.valid_zones:
				if zone == self.hub_zone:
					self.n_charging_poles_by_zone[zone] = self.n_charging_zones
				else:
					self.n_charging_poles_by_zone[zone] = 0

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
