import pandas as pd


class SimStats():

	def __init__ (self):

		self.valid_zones = None
		self.sim_general_conf = None
		self.supply_model_conf = None
		self.grid = None
		self.sim_stats = None

	def get_stats_from_sim (self, sim):

		self.valid_zones = sim.sim_input.valid_zones
		self.sim_general_conf = sim.sim_input.sim_general_conf
		self.supply_model_conf = sim.sim_input.supply_model_conf
		self.grid = sim.sim_input.grid

		# Sim Stats creation

		self.sim_stats = pd.Series(name="sim_stats", dtype=object)

		self.sim_stats = pd.concat([
			self.sim_stats,
			pd.Series(self.supply_model_conf)
		])

		self.sim_stats.loc["n_vehicles_sim"] = sim.sim_input.n_vehicles_sim
		self.sim_stats.loc["tot_n_charging_poles"] = sim.sim_input.tot_n_charging_poles
		self.sim_stats.loc["n_charging_zones"] = sim.sim_input.n_charging_zones

		self.sim_stats["sim_duration"] = (sim.end - sim.start).total_seconds()
		self.sim_stats.loc["tot_potential_charging_energy"] = self.sim_stats.loc["sim_duration"] / 3600 * (
			# TODO -> parametrise rated power
			self.sim_stats.loc["tot_n_charging_poles"] * 3.7
		)

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

		if self.sim_stats["n_unsatisfied"]:
			self.sim_stats.loc["fraction_no_close_vehicles_unsatisfied"] = \
				sim.n_no_close_vehicles / self.sim_stats["n_unsatisfied"]
		else:
			self.sim_stats.loc["fraction_no_close_vehicles_unsatisfied"] = 0

		if self.sim_stats["n_unsatisfied"]:
			self.sim_stats.loc["fraction_deaths_unsatisfied"] = \
				sim.n_deaths / self.sim_stats["n_unsatisfied"]
		else:
			self.sim_stats.loc["fraction_deaths_unsatisfied"] = 0

		self.sim_stats.loc["n_charges"] = sim.charging_strategy.n_charges

		self.sim_stats.loc["tot_mobility_distance"] = sim.tot_mobility_distance
		self.sim_stats.loc["tot_mobility_duration"] = sim.tot_mobility_duration

		if self.supply_model_conf["relocation"]:
			if "relocation" in self.supply_model_conf and self.supply_model_conf["relocation"]:
				self.sim_stats.loc["n_scooter_relocations"] = sim.relocation_strategy.n_scooter_relocations
				self.sim_stats.loc["tot_scooter_relocations_distance"] = \
					sim.relocation_strategy.tot_scooter_relocations_distance
				self.sim_stats.loc["tot_scooter_relocations_duration"] = \
					sim.relocation_strategy.tot_scooter_relocations_duration
				if sim.relocation_strategy.n_scooter_relocations:
					self.sim_stats.loc["avg_n_vehicles_relocated"] = \
						sim.relocation_strategy.n_vehicles_tot / sim.relocation_strategy.n_scooter_relocations
				else:
					self.sim_stats.loc["avg_n_vehicles_relocated"] = 0

				n_workers = 0
				tot_jobs = 0
				max_jobs = float('-inf')
				min_jobs = float('inf')
				for worker in sim.relocation_strategy.relocation_workers:
					n_workers += 1
					tot_jobs += worker.n_jobs
					if worker.n_jobs > max_jobs:
						max_jobs = worker.n_jobs
					if worker.n_jobs < min_jobs:
						min_jobs = worker.n_jobs

				self.sim_stats.loc["avg_jobs_per_worker"] = tot_jobs / n_workers
				self.sim_stats.loc["min_jobs_per_worker"] = min_jobs
				self.sim_stats.loc["max_jobs_per_worker"] = max_jobs

		for metrics, value in sim.sim_metrics.metrics_iter():
			self.sim_stats.loc[metrics] = value
