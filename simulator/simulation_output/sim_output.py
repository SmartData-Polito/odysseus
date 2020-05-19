import datetime
import numpy as np
import pandas as pd

from simulator.simulation.charging_primitives import get_charging_soc
from simulator.utils.vehicle_utils import soc_to_kwh


class EFFCS_SimOutput ():

	def __init__ (self, sim):

		self.sim_general_conf = sim.simInput.sim_general_conf
		self.sim_scenario_conf = sim.simInput.sim_scenario_conf

		self.sim_booking_requests = pd.DataFrame(sim.sim_booking_requests)
		self.sim_bookings = self.sim_booking_requests.dropna()
		self.sim_charges = pd.DataFrame(sim.chargingStrategy.sim_charges)
		self.sim_not_enough_energy_requests = pd.DataFrame(sim.sim_booking_requests_deaths)
		self.sim_no_close_vehicle_requests = pd.DataFrame(sim.sim_no_close_vehicle_requests)
		self.sim_unsatisfied_requests = pd.DataFrame(sim.sim_unsatisfied_requests)
		self.sim_system_charges_bookings = pd.DataFrame(sim.chargingStrategy.list_system_charging_bookings)
		self.n_vehicles_per_zones_history = pd.DataFrame(sim.n_vehicles_per_zones_history)

		self.sim_system_charges_bookings["end_hour"] = self.sim_system_charges_bookings["end_time"].apply(
			lambda d: d.hour
		)

		self.sim_users_charges_bookings = pd.DataFrame\
			(sim.chargingStrategy.list_users_charging_bookings,
			 columns = self.sim_system_charges_bookings.columns)

		self.sim_users_charges_bookings["end_hour"] = \
			self.sim_users_charges_bookings["end_time"].apply\
			(lambda d: d.hour)

		self.sim_unfeasible_charge_bookings = pd.DataFrame(
			sim.chargingStrategy.sim_unfeasible_charge_bookings
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

		self.sim_charge_deaths = pd.DataFrame(sim.chargingStrategy.sim_unfeasible_charge_bookings)

		self.grid = sim.simInput.grid

		# Sim Stats creation

		self.sim_stats = pd.Series(name="sim_stats")

		self.sim_stats = pd.concat([
			self.sim_stats,
			pd.Series(sim.simInput.sim_general_conf)
		])

		self.sim_stats = pd.concat([
			self.sim_stats,
			pd.Series(sim.simInput.sim_scenario_conf)
		])

		self.sim_stats.loc["n_same_zone_trips"] = \
			sim.n_same_zone_trips

		self.sim_stats.loc["n_not_same_zone_trips"] = \
			sim.n_not_same_zone_trips

		self.sim_stats.loc["n_no_close_vehicles"] = \
			sim.n_no_close_vehicles

		self.sim_stats.loc["n_deaths"] = \
			sim.n_deaths

		self.sim_stats["n_booking_reqs"] = \
			self.sim_stats["n_same_zone_trips"]\
			+ self.sim_stats["n_not_same_zone_trips"]\
			+ self.sim_stats["n_no_close_vehicles"]\
			+ self.sim_stats["n_deaths"]

		self.sim_stats["n_bookings"] = \
			self.sim_stats["n_same_zone_trips"]\
			+ self.sim_stats["n_not_same_zone_trips"]

		self.sim_stats["n_unsatisfied"] = \
			self.sim_stats["n_no_close_vehicles"]\
			+ self.sim_stats["n_deaths"]

		self.sim_stats.loc["fraction_satisfied"] = \
			self.sim_stats["n_bookings"] / self.sim_stats["n_booking_reqs"]

		self.sim_stats.loc["fraction_unsatisfied"] = \
			1.0 - self.sim_stats.loc["fraction_satisfied"]

		self.sim_stats.loc["fraction_same_zone_trips"] = \
			sim.n_same_zone_trips / self.sim_stats["n_booking_reqs"]

		self.sim_stats.loc["fraction_not_same_zone_trips"] = \
			sim.n_not_same_zone_trips / self.sim_stats["n_booking_reqs"]

		self.sim_stats.loc["fraction_no_close_vehicles"] = \
			sim.n_no_close_vehicles / self.sim_stats["n_booking_reqs"]

		self.sim_stats.loc["fraction_not_enough_energy"] = \
			sim.n_deaths / self.sim_stats["n_booking_reqs"]

		self.sim_stats.loc["fraction_same_zone_trips_satisfied"] = \
			sim.n_same_zone_trips / self.sim_stats["n_bookings"]

		self.sim_stats.loc["fraction_not_same_zone_trips_satisfied"] = \
			sim.n_not_same_zone_trips / self.sim_stats["n_bookings"]

		self.sim_stats.loc["fraction_no_close_vehicles_unsatisfied"] = \
			sim.n_no_close_vehicles / self.sim_stats["n_unsatisfied"]

		self.sim_stats.loc["fraction_deaths_unsatisfied"] = \
			sim.n_deaths / self.sim_stats["n_unsatisfied"]

		self.sim_stats.loc["n_charges"] = \
			len(self.sim_charges)

		self.sim_stats.loc["n_charging_requests_system"] = \
			len(self.sim_system_charges_bookings)

		self.sim_stats.loc["n_charges_system"] = \
			self.sim_charges.groupby("operator")\
				.date.count().loc["system"]

		self.sim_stats.loc["n_charge_deaths"] = \
			len(self.sim_charge_deaths)

		self.sim_stats.loc["fraction_charge_deaths"] = \
			len(self.sim_charge_deaths) / self.sim_stats.loc["n_charges"]

		self.sim_stats.loc["fraction_charge_deaths_system"] = \
			len(self.sim_charge_deaths) / self.sim_stats.loc["n_charges_system"]

		self.sim_stats.loc["soc_avg"] = \
			self.sim_bookings.start_soc.mean()

		self.sim_stats.loc["soc_med"] = \
			self.sim_bookings.start_soc.median()

		self.sim_stats.loc["charging_time_avg"] = \
			self.sim_charges.duration.mean() / 3600

		self.sim_stats.loc["charging_time_med"] = \
			self.sim_charges.duration.median() / 3600

		self.sim_stats.loc["n_charges_by_vehicle_avg"] = \
			self.sim_charges.groupby("plate").date.count().mean()

		self.sim_stats.loc["n_charges_by_vehicle_system_avg"] = \
			self.sim_charges[self.sim_charges.operator == "system"]\
				.groupby("plate").date.count().mean()

		if len(self.sim_users_charges_bookings):
			self.sim_stats.loc["n_charges_by_vehicle_users_avg"] = \
				self.sim_charges[self.sim_charges.operator == "users"]\
					.groupby("plate").date.count().mean()
		else:
			self.sim_stats.loc["n_charges_by_vehicle_users_avg"] = 0

		self.sim_stats["sim_duration"] = (sim.end - sim.start).total_seconds()

		self.sim_stats.loc["tot_potential_mobility_energy"] = \
			self.sim_booking_requests.soc_delta.sum()

		self.sim_stats.loc["tot_potential_charging_energy"] = \
			get_charging_soc(self.sim_stats["sim_duration"] / 3600)

		self.sim_stats.loc["tot_charging_energy"] = \
			self.sim_charges["soc_delta_kwh"].sum()

		self.sim_stats.loc["fraction_charges_system"] = \
			self.sim_charges.groupby("operator")\
			.date.count().loc["system"]\
			/ len(self.sim_charges)

		if "users" in self.sim_charges.operator.unique():
			self.sim_stats.loc["fraction_charges_users"] = \
				self.sim_charges.groupby("operator")\
				.date.count().loc["users"]\
				/ len(self.sim_charges)
		else:
			self.sim_stats.loc["fraction_charges_users"] = 0

		if "users" in self.sim_charges.operator.unique():
			self.sim_stats.loc["fraction_energy_system"] = \
				self.sim_charges.groupby("operator")\
				.soc_delta_kwh.sum().loc["system"]\
				/ self.sim_stats["tot_charging_energy"]
			self.sim_stats.loc["fraction_energy_users"] = \
				self.sim_charges.groupby("operator")\
				.soc_delta_kwh.sum().loc["users"]\
				/ self.sim_stats["tot_charging_energy"]
		else:
			self.sim_stats.loc["fraction_energy_system"] = 1
			self.sim_stats.loc["fraction_energy_users"] = 0

		if len(self.sim_users_charges_bookings):
			self.sim_stats.loc["fraction_duration_system"] = \
				self.sim_charges.groupby("operator")\
				.duration.sum().loc["system"]\
				/ self.sim_charges.duration.sum()
			self.sim_stats.loc["fraction_duration_users"] = \
				self.sim_charges.groupby("operator")\
				.duration.sum().loc["users"]\
				/ self.sim_charges.duration.sum()
		else:
			self.sim_stats.loc["fraction_duration_system"] = 1
			self.sim_stats.loc["fraction_duration_users"] = 0

		self.sim_stats.loc["charging_duration_avg"] = \
			self.sim_charges.duration.mean()

		self.sim_stats.loc["charging_energy_event_avg"] = \
			self.sim_charges.soc_delta_kwh.mean()

		self.sim_stats.loc["charging_energy_event_max"] = \
			self.sim_charges.soc_delta_kwh.max()

		self.sim_stats.loc["charging_energy_event_med"] = \
			self.sim_charges.soc_delta_kwh.median()

		self.sim_charges["cr_timeout"] = \
			self.sim_charges.timeout_outward\
			+ self.sim_charges.timeout_return

		self.sim_stats.loc["cum_relo_out_t"] = \
			self.sim_charges.timeout_outward.sum() / 60 / 60

		self.sim_stats.loc["cum_relo_ret_t"] = \
			self.sim_charges.timeout_return.sum() / 60 / 60

		self.sim_stats.loc["cum_relo_t"] = \
			self.sim_stats.cum_relo_out_t + \
			self.sim_stats.cum_relo_ret_t

		self.sim_stats.loc["cum_relo_khw"] = \
			self.sim_charges.cr_soc_delta_kwh.sum()

		self.sim_stats.loc["avg_hourly_relo_t"] = \
			self.sim_charges.groupby("hour").cr_timeout.sum().mean()

		self.grid[
			"origin_count"
		] = self.sim_booking_requests.origin_id.value_counts()
		self.grid[
			"destination_count"
		] = self.sim_booking_requests.destination_id.value_counts()
		self.grid[
			"charge_needed_system_zones_count"
		] = self.sim_system_charges_bookings.destination_id.value_counts()
		self.grid[
			"charge_needed_users_zones_count"
		] = self.sim_users_charges_bookings.destination_id.value_counts()
		self.grid[
			"unsatisfied_demand_origins_fraction"
		] = self.sim_unsatisfied_requests.origin_id.value_counts() / len(self.sim_unsatisfied_requests)
		if len(self.sim_not_enough_energy_requests):
			self.grid[
				"not_enough_energy_origins_count"
			] = self.sim_not_enough_energy_requests.origin_id.value_counts()
		if len(self.sim_charge_deaths):
			self.grid[
				"charge_deaths_origins_count"
			] = self.sim_charge_deaths.origin_id.value_counts()

		self.sim_stats.loc["hub_zone"] = sim.simInput.hub_zone

		self.vehicles_history = pd.DataFrame()
		for vehicle in sim.vehicles_list:
			vehicle_df = pd.DataFrame(vehicle.status_dict_list)
			vehicle_df["plate"] = vehicle.plate
			self.vehicles_history = pd.concat([self.vehicles_history, vehicle_df], ignore_index=True)
