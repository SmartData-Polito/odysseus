import os
import pickle
import pandas as pd
import datetime
import pytz

from odysseus.supply_modelling.supply_model import SupplyModel


class SimInput:

	def __init__(self, conf_dict):

		self.sim_general_config = conf_dict["sim_general_conf"]
		self.demand_model_config = conf_dict["demand_model_conf"]
		self.supply_model_config = conf_dict["supply_model_conf"]
		self.city_scenario_folder = conf_dict["city_scenario_folder"]
		supply_model = conf_dict["supply_model_object"]

		self.city = self.sim_general_config["city"]
		self.data_source_id = self.sim_general_config["data_source_id"]

		city_scenario_path = os.path.join(
			os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
			"city_scenario",
			"city_scenarios",
			self.sim_general_config["city"],
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
		self.distance_matrix = pickle.Unpickler(open(os.path.join(city_scenario_path, "distance_matrix.pickle"), "rb")).load()
		self.closest_zones = pickle.Unpickler(open(os.path.join(city_scenario_path, "closest_zones.pickle"), "rb")).load()

		self.grid_crs = str(self.grid.crs)

		self.start = datetime.datetime(
			self.sim_general_config["year"],
			self.sim_general_config["month_start"],
			1, tzinfo=pytz.UTC
		)
		self.end = self.start + datetime.timedelta(hours=self.sim_general_config["max_sim_hours"])

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
			"city_demand_models",
			self.sim_general_config["city"],
			self.city_scenario_folder
		)

		if self.demand_model_config["demand_model_type"] == "trace":
			self.booking_requests_test = pickle.Unpickler(open(os.path.join(city_scenario_path, "bookings_test.pickle"), "rb")).load()
			self.booking_requests_list = self.get_booking_requests_list()

		else:
			self.demand_model = pickle.Unpickler(
				open(os.path.join(demand_model_path, "demand_model.pickle"), "rb")).load()
			if self.demand_model_config["demand_model_type"] == "poisson_kde":
				self.request_rates = pickle.Unpickler(open(os.path.join(demand_model_path, "request_rates.pickle"), "rb")).load()
				self.avg_request_rate = pd.DataFrame(self.request_rates.values()).mean().mean()
				self.trip_kdes = pickle.Unpickler(open(os.path.join(demand_model_path, "trip_kdes.pickle"), "rb")).load()
				self.demand_model.requests_rate_factor = self.demand_model_config["requests_rate_factor"]

		if "n_requests" in self.supply_model_config.keys():
			self.desired_avg_rate = self.supply_model_config["n_requests"] / self.total_days / 24 / 3600
			self.rate_ratio = self.desired_avg_rate / self.avg_request_rate
			self.demand_model_config["requests_rate_factor"] = self.rate_ratio

		self.tot_n_charging_poles = 0
		self.n_charging_zones = 0

		self.n_charging_poles_by_zone = {}
		self.vehicles_soc_dict = {}
		self.vehicles_zones = {}

		self.zones_cp_distances = pd.Series(dtype=float)
		self.closest_cp_zone = pd.Series(dtype=float)

		if supply_model is not None:

			# TODO -> sollevare eccezioni/warning se i parametri non son compatibili
			self.supply_model = supply_model
			self.n_vehicles_sim = supply_model.n_vehicles_sim

		else:

			self.supply_model = SupplyModel(
				self.city, self.data_source_id,
				self.city_scenario_folder, None,
				self.supply_model_config
			)

	def get_booking_requests_list(self):

		self.booking_requests_test["start_time"] = pd.to_datetime(self.booking_requests_test["start_time"])
		self.booking_requests_test["end_time"] = pd.to_datetime(self.booking_requests_test["end_time"])

		return self.booking_requests_test[[
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
		self.supply_model.init_vehicles()
		self.n_vehicles_sim = self.supply_model.n_vehicles_sim
		self.supply_model_config["n_vehicles_sim"] = self.n_vehicles_sim

	def init_charging_poles(self):
		self.supply_model.init_charging_poles()
		self.tot_n_charging_poles = self.supply_model.tot_n_charging_poles
		self.supply_model_config["tot_n_charging_poles"] = self.tot_n_charging_poles
		self.n_charging_zones = self.supply_model.n_charging_zones
		self.supply_model_config["n_charging_zones"] = self.n_charging_zones
		self.closest_cp_zone = self.supply_model.closest_cp_zone

	def init_relocation(self):
		return self.supply_model.init_relocation()

	def init_workers(self):
		pass
