import datetime
import os
import pandas as pd
from odysseus.simulator.simulation_output.sim_stats import SimStats
from odysseus.utils.cost_utils import insert_sim_costs, insert_scenario_costs
from odysseus.supply_modelling.cost_config import *


class SimOutput:

	def __init__(self, sim):

		self.valid_zones = sim.sim_input.valid_zones

		self.sim_general_config = sim.sim_input.sim_general_config
		self.supply_model_config = sim.sim_input.supply_model_config
		self.grid = sim.sim_input.grid
		self.grid = self.grid.loc[:, ~self.grid.columns.duplicated()]
		self.n_charging_poles_by_zone = sim.sim_input.supply_model.n_charging_poles_by_zone

		# Sim Stats creation

		sim_stats_obj = SimStats()
		self.sim_stats = sim_stats_obj.get_stats_from_sim(sim)
		self.sim_stats = sim_stats_obj.sim_stats

		if self.sim_general_config["save_history"]:

			self.sim_booking_requests = pd.DataFrame(sim.sim_booking_requests)
			self.sim_bookings = pd.DataFrame(sim.sim_bookings)

			self.sim_charges = pd.DataFrame(sim.charging_strategy.sim_charges)
			self.sim_not_enough_energy_requests = pd.DataFrame(sim.sim_booking_requests_deaths)
			self.sim_no_close_vehicle_requests = pd.DataFrame(sim.sim_no_close_vehicle_requests)
			self.sim_unsatisfied_requests = pd.DataFrame(sim.sim_unsatisfied_requests)
			self.sim_system_charges_bookings = pd.DataFrame(sim.charging_strategy.list_system_charging_bookings)
			self.sim_users_charges_bookings = pd.DataFrame(sim.charging_strategy.list_users_charging_bookings)

			if "end_time" not in self.sim_system_charges_bookings:
				self.sim_system_charges_bookings["end_time"] = pd.Series(dtype=object)
			if "end_time" not in self.sim_users_charges_bookings:
				self.sim_users_charges_bookings["end_time"] = pd.Series(dtype=object)

			if len(self.sim_system_charges_bookings):
				self.sim_system_charges_bookings["end_hour"] = self.sim_system_charges_bookings["end_time"].apply(
					lambda d: d.hour
				)

			if len(self.sim_users_charges_bookings):
				self.sim_users_charges_bookings["end_hour"] = self.sim_users_charges_bookings["end_time"].apply(
					lambda d: d.hour
				)

			self.sim_unfeasible_charge_bookings = pd.DataFrame(
				sim.charging_strategy.sim_unfeasible_charge_bookings
			)

			self.sim_booking_requests["n_vehicles_charging_system"] = \
				pd.Series(sim.list_n_vehicles_charging_system)

			self.sim_booking_requests["n_vehicles_charging_users"] = \
				pd.Series(sim.list_n_vehicles_charging_users).fillna(0)

			self.sim_booking_requests["n_vehicles_available"] = \
				pd.Series(sim.list_n_vehicles_available)

			self.sim_booking_requests["n_vehicles_booked"] = \
				pd.Series(sim.list_n_vehicles_booked)

			self.sim_booking_requests["n_vehicles_dead"] = \
				pd.Series(sim.list_n_vehicles_dead)

			self.sim_charge_deaths = pd.DataFrame(sim.charging_strategy.sim_unfeasible_charge_bookings)

			self.sim_stats.loc["n_charging_requests_system"] = len(self.sim_system_charges_bookings)

			if len(self.sim_charges) and "system" in self.sim_charges.operator:
				self.sim_stats.loc["n_charges_system"] = self.sim_charges.groupby("operator").date.count().loc["system"]
			else:
				self.sim_stats.loc["n_charges_system"] = 0

			if len(self.sim_charges) and "users" in self.sim_charges.operator:
				self.sim_stats.loc["n_charges_users"] = self.sim_charges.groupby("operator").date.count().loc["users"]
			else:
				self.sim_stats.loc["n_charges_users"] = 0

			self.sim_stats.loc["n_charge_deaths"] = \
				len(self.sim_charge_deaths)

			if len(self.sim_charges):
				self.sim_stats.loc["fraction_charge_deaths"] = \
					len(self.sim_charge_deaths) / self.sim_stats.loc["n_charges"]
			else:
				self.sim_stats.loc["fraction_charge_deaths"] = 0

			if len(self.sim_bookings):
				self.sim_stats.loc["soc_avg"] = \
					self.sim_bookings.start_soc.mean()
			else:
				self.sim_stats.loc["soc_avg"] = 0

			if len(self.sim_bookings):
				self.sim_stats.loc["soc_med"] = \
					self.sim_bookings.start_soc.median()
			else:
				self.sim_stats.loc["soc_med"] = 0

			if len(self.sim_charges):
				self.sim_stats.loc["charging_time_avg"] = \
					self.sim_charges.duration.mean() / 3600

				self.sim_stats.loc["charging_time_med"] = \
					self.sim_charges.duration.median() / 3600

				self.sim_stats.loc["n_charges_by_vehicle_avg"] = \
					self.sim_charges.groupby("plate").date.count().mean()

				self.sim_stats.loc["n_charges_by_vehicle_system_avg"] = \
					self.sim_charges[self.sim_charges.operator == "system"] \
						.groupby("plate").date.count().mean()
			else:
				self.sim_stats.loc["charging_time_avg"] = 0
				self.sim_stats.loc["charging_time_med"] = 0
				self.sim_stats.loc["n_charges_by_vehicle_avg"] = 0
				self.sim_stats.loc["n_charges_by_vehicle_system_avg"] = 0

			if len(self.sim_users_charges_bookings):
				self.sim_stats.loc["n_charges_by_vehicle_users_avg"] = \
					self.sim_charges[self.sim_charges.operator == "users"] \
						.groupby("plate").date.count().mean()
			else:
				self.sim_stats.loc["n_charges_by_vehicle_users_avg"] = 0

			if len(self.sim_bookings):
				self.sim_stats.loc["tot_potential_mobility_distance"] = self.sim_booking_requests.driving_distance.sum()
				self.sim_stats.loc["tot_potential_mobility_duration"] = self.sim_booking_requests.duration.sum()
				self.sim_stats.loc["tot_potential_welltotank_energy"] = self.sim_booking_requests.welltotank_kwh.sum()
				self.sim_stats.loc["tot_potential_tanktowheel_energy"] = self.sim_booking_requests.tanktowheel_kwh.sum()
				self.sim_stats.loc["tot_potential_mobility_energy"] = self.sim_booking_requests.soc_delta_kwh.sum()
				self.sim_stats.loc[
					"tot_potential_welltotank_co2_emissions"] = self.sim_booking_requests.welltotank_emissions.sum() / 1000
				self.sim_stats.loc[
					"tot_potential_welltowheel_co2_emissions"] = self.sim_booking_requests.tanktowheel_emissions.sum() / 1000
				self.sim_stats.loc["tot_potential_co2_emissions_kg"] = self.sim_booking_requests.co2_emissions.sum() / 1000

			if len(self.sim_bookings):
				self.sim_stats.loc["tot_mobility_distance"] = self.sim_bookings.driving_distance.sum()
				self.sim_stats.loc["tot_mobility_duration"] = self.sim_bookings.duration.sum()
				self.sim_stats.loc["tot_welltotank_energy"] = self.sim_bookings.welltotank_kwh.sum()
				self.sim_stats.loc["tot_tanktowheel_energy"] = self.sim_bookings.tanktowheel_kwh.sum()
				self.sim_stats.loc["tot_mobility_energy"] = self.sim_bookings.soc_delta_kwh.sum()
				self.sim_stats.loc["tot_welltotank_co2_emissions"] = self.sim_bookings.welltotank_emissions.sum() / 1000
				self.sim_stats.loc["tot_tanktowheel_co2_emissions"] = self.sim_bookings.tanktowheel_emissions.sum() / 1000
				self.sim_stats.loc["tot_co2_emissions_kg"] = self.sim_bookings.co2_emissions.sum() / 1000

			if len(self.sim_charges):
				self.sim_stats.loc["tot_charging_energy"] = self.sim_charges["soc_delta_kwh"].sum()
			else:
				self.sim_stats.loc["tot_charging_energy"] = 0

			self.sim_stats.loc["tot_charging_return_distance"] = sim.charging_strategy.charging_return_distance

			if len(self.sim_charges) and "system" in self.sim_charges.operator.unique():
				self.sim_stats.loc["fraction_charges_system"] = \
					self.sim_charges.groupby("operator") \
						.date.count().loc["system"] \
					/ len(self.sim_charges)
				self.sim_stats.loc["fraction_energy_system"] = \
					self.sim_charges.groupby("operator") \
						.soc_delta_kwh.sum().loc["system"] \
					/ self.sim_stats["tot_charging_energy"]
				self.sim_stats.loc["fraction_duration_system"] = \
					self.sim_charges.groupby("operator") \
						.duration.sum().loc["system"] \
					/ self.sim_charges.duration.sum()
			else:
				self.sim_stats.loc["fraction_charges_system"] = 0
				self.sim_stats.loc["fraction_energy_system"] = 0
				self.sim_stats.loc["fraction_duration_system"] = 0

			if len(self.sim_charges) and "users" in self.sim_charges.operator.unique():
				self.sim_stats.loc["fraction_charges_users"] = \
					self.sim_charges.groupby("operator") \
						.date.count().loc["users"] \
					/ len(self.sim_charges)
				self.sim_stats.loc["fraction_energy_users"] = \
					self.sim_charges.groupby("operator") \
						.soc_delta_kwh.sum().loc["users"] \
					/ self.sim_stats["tot_charging_energy"]
				self.sim_stats.loc["fraction_duration_users"] = \
					self.sim_charges.groupby("operator") \
						.duration.sum().loc["users"] \
					/ self.sim_charges.duration.sum()
			else:
				self.sim_stats.loc["fraction_charges_users"] = 0
				self.sim_stats.loc["fraction_energy_users"] = 0
				self.sim_stats.loc["fraction_duration_users"] = 0

			if len(self.sim_charges):
				self.sim_stats.loc["charging_duration_avg"] = \
					self.sim_charges.duration.mean()

				self.sim_stats.loc["charging_energy_event_avg"] = \
					self.sim_charges.soc_delta_kwh.mean()

				self.sim_stats.loc["charging_energy_event_max"] = \
					self.sim_charges.soc_delta_kwh.max()

				self.sim_stats.loc["charging_energy_event_med"] = \
					self.sim_charges.soc_delta_kwh.median()

				self.sim_charges["cr_timeout"] = \
					self.sim_charges.timeout_outward \
					+ self.sim_charges.timeout_return

				self.sim_stats.loc["cum_relo_out_t"] = \
					self.sim_charges.timeout_outward.sum()

				self.sim_stats.loc["cum_relo_ret_t"] = \
					self.sim_charges.timeout_return.sum()

				self.sim_stats.loc["cum_relo_t"] = \
					self.sim_stats.cum_relo_out_t + \
					self.sim_stats.cum_relo_ret_t

				self.sim_stats.loc["cum_relo_khw"] = \
					self.sim_charges.cr_soc_delta_kwh.sum()

				self.sim_stats.loc["avg_hourly_relo_t"] = \
					self.sim_charges.groupby("hour").cr_timeout.sum().mean()
			else:

				self.sim_stats.loc["charging_duration_avg"] = 0
				self.sim_stats.loc["charging_energy_event_avg"] = 0
				self.sim_stats.loc["charging_energy_event_max"] = 0
				self.sim_stats.loc["charging_energy_event_med"] = 0
				self.sim_charges["cr_timeout"] = 0
				self.sim_stats.loc["cum_relo_out_t"] = 0
				self.sim_stats.loc["cum_relo_ret_t"] = 0
				self.sim_stats.loc["cum_relo_t"] = 0
				self.sim_stats.loc["cum_relo_khw"] = 0
				self.sim_stats.loc["avg_hourly_relo_t"] = 0

			self.grid[
				"origin_count"
			] = self.sim_booking_requests.origin_id.value_counts()
			self.grid[
				"destination_count"
			] = self.sim_booking_requests.destination_id.value_counts()

			if len(self.sim_system_charges_bookings):
				self.grid[
					"charge_needed_system_zones_count"
				] = self.sim_system_charges_bookings.destination_id.value_counts()
			else:
				self.grid[
					"charge_needed_system_zones_count"
				] = 0
			if len(self.sim_users_charges_bookings):
				self.grid[
					"charge_needed_users_zones_count"
				] = self.sim_users_charges_bookings.destination_id.value_counts()
			else:
				self.grid[
					"charge_needed_users_zones_count"
				] = 0

			if self.sim_stats["n_unsatisfied"]:
				self.grid[
					"unsatisfied_demand_origins"
				] = self.sim_unsatisfied_requests.origin_id.value_counts()
			else:
				self.grid[
					"unsatisfied_demand_origins"
				] = 0

			if len(self.sim_not_enough_energy_requests):
				self.grid[
					"not_enough_energy_origins_count"
				] = self.sim_not_enough_energy_requests.origin_id.value_counts()
			if len(self.sim_charge_deaths):
				self.grid[
					"charge_deaths_origins_count"
				] = self.sim_charge_deaths.origin_id.value_counts()

			self.sim_stats.loc["max_driving_distance"] = self.sim_booking_requests.driving_distance.max()

			self.vehicles_history = pd.DataFrame()
			for vehicle in sim.vehicles_list:
				vehicle_df = pd.DataFrame(vehicle.status_dict_list)
				vehicle_df["plate"] = vehicle.plate
				self.vehicles_history = pd.concat([self.vehicles_history, vehicle_df], ignore_index=True)

			self.stations_history = pd.DataFrame()
			for key in sim.charging_strategy.charging_stations_dict:
				station_df = pd.DataFrame(sim.charging_strategy.charging_stations_dict[key].status_dict_list)
				station_df["id"] = key
				self.stations_history = pd.concat([self.stations_history, station_df], ignore_index=True)

			self.zones_history = pd.DataFrame()
			for key in sim.charging_strategy.zone_dict:
				zone_df = pd.DataFrame(sim.charging_strategy.zone_dict[key].status_dict_list)
				zone_df["zone_id"] = key
				self.zones_history = pd.concat([self.zones_history, zone_df], ignore_index=True)

			if self.supply_model_config["relocation"]:
				self.relocation_history = pd.DataFrame(sim.relocation_strategy.sim_scooter_relocations)

		for key in self.sim_stats.index:
			if key.startswith("fraction"):
				self.sim_stats["percentage" + key[8:]] = self.sim_stats[key] * 100

		if self.sim_general_config["save_history"]:

			insert_scenario_costs(self.sim_stats, self.supply_model_config, vehicle_cost, charging_station_costs)
			insert_sim_costs(self.sim_stats, self.supply_model_config, fuel_costs, administrative_cost_conf, vehicle_cost)
			self.sim_stats.loc[
				"profit"
			] = self.sim_stats["revenues"] - self.sim_stats["scenario_cost"] - self.sim_stats["sim_cost"]

	def save_output(self, results_path, sim_general_conf, sim_scenario_conf):

		if sim_general_conf["history_to_file"]:

			if not sim_general_conf["exclude_events_files"]:

				self.sim_booking_requests.to_csv(
					os.path.join(
						results_path,
						"sim_booking_requests.csv"
					)
				)
				self.sim_bookings.to_csv(
					os.path.join(
						results_path,
						"sim_bookings.csv"
					)
				)
				self.sim_charges.to_csv(
					os.path.join(
						results_path,
						"sim_charges.csv"
					)
				)
				self.sim_not_enough_energy_requests.to_csv(
					os.path.join(
						results_path,
						"sim_unsatisfied_no_energy.csv"
					)
				)
				self.sim_no_close_vehicle_requests.to_csv(
					os.path.join(
						results_path,
						"sim_unsatisfied_no_close_vehicle.csv"
					)
				)
				self.sim_unsatisfied_requests.to_csv(
					os.path.join(
						results_path,
						"sim_unsatisfied_requests.csv"
					)
				)
				self.sim_system_charges_bookings.to_csv(
					os.path.join(
						results_path,
						"sim_system_charges_bookings.csv"
					)
				)

				self.sim_users_charges_bookings.to_csv(
					os.path.join(
						results_path,
						"sim_users_charges_bookings.csv"
					)
				)
				self.sim_unfeasible_charge_bookings.to_csv(
					os.path.join(
						results_path,
						"sim_unfeasible_charge_bookings.csv"
					)
				)
				self.sim_charge_deaths.to_csv(
					os.path.join(
						results_path,
						"sim_unfeasible_charges.csv"
					)
				)

			if not sim_general_conf["exclude_resources_files"]:

				self.vehicles_history.to_csv(
					os.path.join(
						results_path,
						"vehicles_history.csv"
					)
				)

				self.stations_history.to_csv(
					os.path.join(
						results_path,
						"stations_history.csv"
					)
				)

				self.zones_history.to_csv(
					os.path.join(
						results_path,
						"zones_history.csv"
					)
				)

			if sim_scenario_conf["relocation"]:
				self.relocation_history.to_csv(
					os.path.join(
						results_path,
						"relocation_history.csv"
					)
				)
