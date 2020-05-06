import numpy as np
import pandas as pd
from sklearn.neighbors import KernelDensity

from simulator.utils.vehicle_utils import get_soc_delta


class EFFCS_SimInput ():

	def __init__ (self,
				  conf_tuple):

		self.sim_general_conf = conf_tuple[0]
		self.sim_scenario_conf = conf_tuple[1]
		self.city_obj = conf_tuple[2]

		self.city = self.city_obj.city_name
		self.grid = self.city_obj.grid
		self.bookings = self.city_obj.bookings
		self.input_bookings = self.city_obj.input_bookings
		self.request_rates = self.city_obj.request_rates
		self.trip_kdes = self.city_obj.trip_kdes
		self.valid_zones = self.city_obj.valid_zones
		self.od_distances = self.city_obj.od_distances
		self.neighbors = self.city_obj.neighbors
		self.neighbors_dict = self.city_obj.neighbors_dict

		self.n_vehicles_original = self.sim_general_conf["n_vehicles_original"]
		self.n_vehicles_sim = int(abs(self.n_vehicles_original * self.sim_scenario_conf["n_vehicles_factor"]))
		self.n_charging_zones = int(self.sim_scenario_conf["cps_zones_percentage"] * len(self.valid_zones))

		self.hub_zone = -1

		if self.sim_scenario_conf["hub"] and not self.sim_scenario_conf["distributed_cps"]:
			self.hub_n_charging_poles = int(abs(self.n_vehicles_sim * self.sim_scenario_conf["n_poles_n_vehicles_factor"]))
			self.n_charging_poles = self.hub_n_charging_poles

		elif not self.sim_scenario_conf["hub"] and self.sim_scenario_conf["distributed_cps"]:
			self.hub_n_charging_poles = 0
			self.n_charging_poles = int(abs(self.n_vehicles_sim * self.sim_scenario_conf["n_poles_n_vehicles_factor"]))

		elif self.sim_scenario_conf["hub"] and self.sim_scenario_conf["distributed_cps"]:

			self.n_charging_poles = \
				int(abs(self.n_vehicles_sim * self.sim_scenario_conf["n_poles_n_vehicles_factor"])) / 2

			self.hub_n_charging_poles = \
				int(abs(self.n_vehicles_sim * self.sim_scenario_conf["n_poles_n_vehicles_factor"])) / 2

		if self.sim_scenario_conf["alpha"] == "auto":
			self.sim_scenario_conf["alpha"] = np.ceil(get_soc_delta(self.od_distances.max().max() / 1000))

	def get_booking_requests_list (self):

		self.booking_requests_list = self.input_bookings[[
			"origin_id",
			"destination_id",
			"start_time",
			"end_time",
			"ia_timeout",
			"euclidean_distance",
			"day",
			"hour",
			"minute",
			"duration",
			"soc_delta"
		]].dropna().to_dict("records")
		return self.booking_requests_list

	def init_vehicles (self):

		vehicles_random_soc = list(
			np.random.uniform(25, 100, self.n_vehicles_sim).astype(int)
		)

		self.vehicles_soc_dict = {
			i: vehicles_random_soc[i] for i in range(self.n_vehicles_sim)
		}

		top_o_zones = self.input_bookings .origin_id.value_counts().iloc[:50].index

		vehicles_random_zones = list(
			np.random.uniform(0, 50, self.n_vehicles_sim).astype(int)
		)

		self.vehicles_zones = [
			self.grid.loc[top_o_zones[i]].zone_id
			for i in vehicles_random_zones
		]

		self.vehicles_zones = {
			i: self.vehicles_zones[i] for i in range(self.n_vehicles_sim)
		}

		return self.vehicles_soc_dict, self.vehicles_zones

	def init_vehicles_dicts (self):

		self.available_vehicles_dict = {int(zone):[] for zone in self.grid.zone_id}

		for vehicle in range(len(self.vehicles_zones)):
			zone = self.vehicles_zones[vehicle]
			self.available_vehicles_dict[zone] += [vehicle]

		return self.available_vehicles_dict

	def init_hub (self):


		if self.sim_scenario_conf["hub_zone_policy"] == "manual":
			pass

		if self.sim_scenario_conf["hub_zone_policy"] == "num_parkings":
			self.hub_zone = int(self.input_bookings.destination_id.value_counts().iloc[:1].index[0])

	def init_charging_poles (self):

		if self.sim_scenario_conf["distributed_cps"]\
		and self.sim_scenario_conf["cps_placement_policy"] == "num_parkings":

			top_dest_zones = self.input_bookings.destination_id.value_counts().iloc[:self.n_charging_zones]

			self.n_charging_poles_by_zone = dict((top_dest_zones / top_dest_zones.sum() * self.n_charging_poles))

			assigned_cps = 0
			for zone_id in self.n_charging_poles_by_zone:
				zone_n_cps = int(np.floor(self.n_charging_poles_by_zone[zone_id]))
				assigned_cps += zone_n_cps
				self.n_charging_poles_by_zone[zone_id] = \
					zone_n_cps
			for zone_id in self.n_charging_poles_by_zone:
				if assigned_cps < self.n_charging_poles:
					self.n_charging_poles_by_zone[zone_id] += 1
					assigned_cps += 1

			self.n_charging_poles_by_zone = \
				dict(pd.Series\
				(self.n_charging_poles_by_zone)\
				.replace({0:np.NaN}).dropna())

			zones_with_cps = pd.Series\
				(self.n_charging_poles_by_zone).index

			self.zones_cp_distances = \
				self.grid.centroid.apply\
				(lambda x: self.grid.loc[zones_with_cps]\
				 .centroid.distance(x))

			self.closest_cp_zone = \
				self.zones_cp_distances.idxmin(axis=1)

			return self.n_charging_poles_by_zone

	def init_relocation (self):
		pass

	def init_workers (self):
		pass
