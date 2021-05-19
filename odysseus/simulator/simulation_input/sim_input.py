import os
import pickle
import pandas as pd


from odysseus.supply_modelling.supply_model import SupplyModel


class SimInput:

	def __init__(self, conf_tuple):

		self.demand_model_config = conf_tuple[0]
		self.sim_scenario_conf = conf_tuple[1]

		if len(conf_tuple) == 3:
			supply_model = conf_tuple[2]
		else:
			supply_model = None

		self.city = self.demand_model_config["city"]

		demand_model_path = os.path.join(
			os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
			"demand_modelling",
			"demand_models",
			self.demand_model_config["city"],
		)

		#demand modelling
		self.grid = pickle.Unpickler(open(os.path.join(demand_model_path, "grid.pickle"), "rb")).load()
		self.grid_matrix = pickle.Unpickler(open(os.path.join(demand_model_path, "grid_matrix.pickle"), "rb")).load()
		self.avg_out_flows_train = pickle.Unpickler(open(os.path.join(demand_model_path, "avg_out_flows_train.pickle"), "rb")).load()
		self.avg_in_flows_train = pickle.Unpickler(open(os.path.join(demand_model_path, "avg_in_flows_train.pickle"), "rb")).load()
		self.valid_zones = pickle.Unpickler(open(os.path.join(demand_model_path, "valid_zones.pickle"), "rb")).load()
		self.neighbors_dict = pickle.Unpickler(open(os.path.join(demand_model_path, "neighbors_dict.pickle"), "rb")).load()
		self.integers_dict = pickle.Unpickler(open(os.path.join(demand_model_path, "integers_dict.pickle"), "rb")).load()
		self.closest_valid_zone = pickle.Unpickler(open(os.path.join(demand_model_path, "closest_valid_zone.pickle"), "rb")).load()


		self.avg_request_rate = self.integers_dict["avg_request_rate"]
		self.n_vehicles_original = self.integers_dict["n_vehicles_original"]
		self.avg_speed_mean = self.integers_dict["avg_speed_mean"]
		self.avg_speed_std = self.integers_dict["avg_speed_std"]
		self.avg_speed_kmh_mean = self.integers_dict["avg_speed_kmh_mean"]
		self.avg_speed_kmh_std = self.integers_dict["avg_speed_kmh_std"]
		self.max_driving_distance = self.integers_dict["max_driving_distance"]

		self.max_in_flow = self.integers_dict["max_in_flow"]
		self.max_out_flow = self.integers_dict["max_out_flow"]

		if self.demand_model_config["sim_technique"] == "traceB":
			self.bookings = pickle.Unpickler(open(os.path.join(demand_model_path, "bookings_test.pickle"), "rb")).load()
			self.booking_requests_list = self.get_booking_requests_list()
		elif self.demand_model_config["sim_technique"] == "eventG":
			self.request_rates = pickle.Unpickler(open(os.path.join(demand_model_path, "request_rates.pickle"), "rb")).load()
			self.trip_kdes = pickle.Unpickler(open(os.path.join(demand_model_path, "trip_kdes.pickle"), "rb")).load()

		#supply model
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
			elif self.sim_scenario_conf["cps_placement_policy"] == "real_positions":
				self.n_charging_zones = 0
		elif self.sim_scenario_conf["battery_swap"]:
			self.n_charging_zones = 0
			self.tot_n_charging_poles = 0

		self.n_charging_poles_by_zone = {}
		self.vehicles_soc_dict = {}
		self.vehicles_zones = {}

		self.start = None

		self.zones_cp_distances = pd.Series()
		self.closest_cp_zone = pd.Series()

		self.supply_model_conf = dict()
		self.supply_model_conf.update(self.sim_scenario_conf)
		self.supply_model_conf.update({
			"city": self.city,
			"data_source_id": self.demand_model_config['data_source_id'],
			"n_vehicles": self.n_vehicles_sim,
			"tot_n_charging_poles": self.tot_n_charging_poles,
			"n_charging_zones": self.n_charging_zones,
		})

		if supply_model is not None:
			#nel caso venga fornito un supply model questo sovrascrive tutto. Eventualmente sollevare eccezioni/warning se i parametri non son compatibili
			self.supply_model = supply_model
			self.n_vehicles_sim = supply_model.n_vehicles_sim
		else:
			self.supply_model = SupplyModel(self.supply_model_conf,self.demand_model_config["year"])


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
