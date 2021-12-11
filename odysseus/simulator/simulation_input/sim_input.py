import os
import pickle
import pandas as pd
import datetime
import pytz

from odysseus.supply_modelling.supply_model import SupplyModel


class SimInput:

	def __init__(self, conf_dict):

		self.sim_general_conf = conf_dict["sim_general_conf"]
		self.demand_model_conf = conf_dict["demand_model_conf"]
		self.supply_model_conf = conf_dict["supply_model_conf"]
		self.city_scenario_folder = conf_dict["city_scenario_folder"]
		supply_model = conf_dict["supply_model_object"]

		self.city = self.sim_general_conf["city"]
		self.data_source_id = self.sim_general_conf["data_source_id"]

		city_scenario_path = os.path.join(
			os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
			"city_scenario",
			"city_scenarios",
			self.sim_general_conf["city"],
			self.city_scenario_folder
		)

		self.grid = pickle.Unpickler(open(os.path.join(city_scenario_path, "grid.pickle"), "rb")).load()
		self.grid_matrix = pickle.Unpickler(open(os.path.join(city_scenario_path, "grid_matrix.pickle"), "rb")).load()
		self.avg_out_flows_train = pickle.Unpickler(open(os.path.join(city_scenario_path, "avg_out_flows_train.pickle"), "rb")).load()
		self.avg_in_flows_train = pickle.Unpickler(open(os.path.join(city_scenario_path, "avg_in_flows_train.pickle"), "rb")).load()
		self.valid_zones = pickle.Unpickler(open(os.path.join(city_scenario_path, "valid_zones.pickle"), "rb")).load()
		self.neighbors_dict = pickle.Unpickler(open(os.path.join(city_scenario_path, "neighbors_dict.pickle"), "rb")).load()
		self.integers_dict = pickle.Unpickler(open(os.path.join(city_scenario_path, "numerical_params_dict.pickle"), "rb")).load()
		self.closest_valid_zone = pickle.Unpickler(open(os.path.join(city_scenario_path, "closest_valid_zone.pickle"), "rb")).load()

		self.distance_matrix = self.grid.loc[self.valid_zones].to_crs("epsg:3857").centroid.apply(
			lambda x: self.grid.loc[self.valid_zones].to_crs("epsg:3857").centroid.distance(x).sort_values()
		)
		self.closest_zones = dict()
		for zone_id in self.valid_zones:
			self.closest_zones[zone_id] = list(
				self.distance_matrix[self.distance_matrix > 0].loc[zone_id].sort_values().dropna().index.values
			)

		self.start = datetime.datetime(
			self.sim_general_conf["year"],
			self.sim_general_conf["month_start"],
			1, tzinfo=pytz.UTC
		)
		if self.sim_general_conf["month_end"] == 12:
			self.end = datetime.datetime(
				self.sim_general_conf["year"] + 1,
				1, 1, tzinfo=pytz.UTC
			)
		else:
			self.end = datetime.datetime(
				self.sim_general_conf["year"],
				self.sim_general_conf["month_end"] + 1,
				1, tzinfo=pytz.UTC
			)
		assert self.end > self.start

		self.total_seconds = (self.end - self.start).total_seconds()
		self.total_days = self.total_seconds / 60 / 60 / 24

		# demand
		self.n_vehicles_original = self.integers_dict["n_vehicles_original"]
		self.avg_speed_mean = self.integers_dict["avg_speed_mean"]
		self.avg_speed_std = self.integers_dict["avg_speed_std"]
		self.avg_speed_kmh_mean = self.integers_dict["avg_speed_kmh_mean"]
		self.avg_speed_kmh_std = self.integers_dict["avg_speed_kmh_std"]
		self.max_driving_distance = self.integers_dict["max_driving_distance"]

		self.max_in_flow = self.integers_dict["max_in_flow"]
		self.max_out_flow = self.integers_dict["max_out_flow"]

		demand_model_path = os.path.join(
			os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
			"demand_modelling",
			"demand_models",
			self.sim_general_conf["city"],
			self.city_scenario_folder
		)

		if self.sim_general_conf["sim_technique"] == "traceB":
			self.bookings = pickle.Unpickler(open(os.path.join(city_scenario_path, "bookings_test.pickle"), "rb")).load()
			self.booking_requests_list = self.get_booking_requests_list()
		elif self.sim_general_conf["sim_technique"] == "eventG":
			self.request_rates = pickle.Unpickler(open(os.path.join(demand_model_path, "request_rates.pickle"), "rb")).load()
			self.avg_request_rate = pd.DataFrame(self.request_rates.values()).mean().mean()
			self.trip_kdes = pickle.Unpickler(open(os.path.join(demand_model_path, "trip_kdes.pickle"), "rb")).load()

		if "n_requests" in self.supply_model_conf.keys():
			self.desired_avg_rate = self.supply_model_conf["n_requests"] / self.total_days / 24 / 3600
			self.rate_ratio = self.desired_avg_rate / self.avg_request_rate
			self.demand_model_conf["requests_rate_factor"] = self.rate_ratio

		# supply
		if "n_vehicles" in self.supply_model_conf.keys():
			self.n_vehicles_sim = self.supply_model_conf["n_vehicles"]
		elif "n_vehicles_factor" in self.supply_model_conf.keys():
			self.n_vehicles_sim = int(
				self.n_vehicles_original * self.supply_model_conf["n_vehicles_factor"]
			)
		elif "fleet_load_factor" in self.supply_model_conf.keys():
			self.n_vehicles_sim = int(
				self.demand_model_conf["n_requests"] / self.supply_model_conf["fleet_load_factor"]
			)

		if "tot_n_charging_poles" in self.supply_model_conf.keys():
			self.tot_n_charging_poles = self.supply_model_conf["tot_n_charging_poles"]
		elif "n_poles_n_vehicles_factor" in self.supply_model_conf.keys():
			self.tot_n_charging_poles = abs(
					self.n_vehicles_sim * self.supply_model_conf["n_poles_n_vehicles_factor"]
			)
		elif self.supply_model_conf["cps_placement_policy"] == "old_manual":
			self.tot_n_charging_poles = len(self.supply_model_conf["cps_zones"]) * 4

		if self.supply_model_conf["distributed_cps"]:
			if "cps_zones_percentage" in self.supply_model_conf and self.supply_model_conf["cps_placement_policy"] != "real_positions":
				self.n_charging_zones = int(self.supply_model_conf["cps_zones_percentage"] * len(self.valid_zones))
			elif "n_charging_zones" in self.supply_model_conf and self.supply_model_conf["cps_placement_policy"] != "real_positions":
				if self.supply_model_conf["n_charging_zones"] > len(self.valid_zones):
					self.supply_model_conf["n_charging_zones"] = len(self.valid_zones)
				self.n_charging_zones = self.supply_model_conf["n_charging_zones"]
				self.supply_model_conf["cps_zones_percentage"] = 1 / len(self.valid_zones)
			elif "cps_zones" in self.supply_model_conf and self.supply_model_conf["cps_placement_policy"] != "real_positions":
				self.n_charging_zones = len(self.supply_model_conf["cps_zones"])
			elif self.supply_model_conf["cps_placement_policy"] == "real_positions":
				self.n_charging_zones = 0
		elif self.supply_model_conf["battery_swap"]:
			self.n_charging_zones = 0
			self.tot_n_charging_poles = 0

		self.n_charging_poles_by_zone = {}
		self.vehicles_soc_dict = {}
		self.vehicles_zones = {}

		self.zones_cp_distances = pd.Series()
		self.closest_cp_zone = pd.Series()

		if supply_model is not None:

			# TODO -> sollevare eccezioni/warning se i parametri non son compatibili
			self.supply_model = supply_model
			self.n_vehicles_sim = supply_model.n_vehicles_sim

		else:

			self.supply_model_conf.update(
				city=self.city,
				data_source_id=self.data_source_id,
				n_vehicles=self.n_vehicles_sim,
				tot_n_charging_poles=self.tot_n_charging_poles,
				n_charging_zones=self.n_charging_zones,
				city_scenario_folder=self.city_scenario_folder,
			)

			self.supply_model = SupplyModel(
				self.city, self.data_source_id,
				self.city_scenario_folder, None,
				self.supply_model_conf
			)

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
			"duration",
		]].dropna().to_dict("records")

	def init_vehicles(self):
		return self.supply_model.init_vehicles()

	def init_charging_poles(self):
		return self.supply_model.init_charging_poles()

	def init_relocation(self):
		return self.supply_model.init_relocation()

	def init_workers(self):
		pass
