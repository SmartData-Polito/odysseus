import pandas as pd



class SimStats():

	def __init__ (self):
		pass


	def get_stats_from_sim (self, sim):

		self.valid_zones = sim.simInput.valid_zones

		self.sim_general_conf = sim.simInput.demand_model_config
		self.sim_scenario_conf = sim.simInput.supply_model_conf

		self.grid = sim.simInput.grid

		# Sim Stats creation

		self.sim_stats = pd.Series(name="sim_stats")

		self.sim_stats = pd.concat([
			self.sim_stats,
			pd.Series(sim.simInput.demand_model_config)
		])

		self.sim_stats = pd.concat([
			self.sim_stats,
			pd.Series(sim.simInput.supply_model_conf)
		])

		self.sim_stats.loc["n_vehicles_sim"] = sim.simInput.n_vehicles_sim
		self.sim_stats.loc["tot_n_charging_poles"] = sim.simInput.tot_n_charging_poles
		self.sim_stats.loc["n_charging_zones"] = sim.simInput.n_charging_zones

		self.sim_stats["sim_duration"] = (sim.end - sim.start).total_seconds()
		self.sim_stats.loc["tot_potential_charging_energy"] = self.sim_stats.loc["sim_duration"] / 3600 * (
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

		self.sim_stats.loc["n_charges"] = sim.chargingStrategy.n_charges

		self.sim_stats.loc["tot_mobility_distance"] = sim.tot_mobility_distance
		self.sim_stats.loc["tot_mobility_duration"] = sim.tot_mobility_duration

		if self.sim_scenario_conf["scooter_relocation"]:
			if "scooter_relocation" in self.sim_scenario_conf and self.sim_scenario_conf["scooter_relocation"]:
				self.sim_stats.loc["n_scooter_relocations"] = sim.scooterRelocationStrategy.n_scooter_relocations
				self.sim_stats.loc["tot_scooter_relocations_distance"] = \
					sim.scooterRelocationStrategy.tot_scooter_relocations_distance
				self.sim_stats.loc["tot_scooter_relocations_duration"] = \
					sim.scooterRelocationStrategy.tot_scooter_relocations_duration
				if sim.scooterRelocationStrategy.n_scooter_relocations:
					self.sim_stats.loc["avg_n_vehicles_relocated"] = \
						sim.scooterRelocationStrategy.n_vehicles_tot / sim.scooterRelocationStrategy.n_scooter_relocations
				else:
					self.sim_stats.loc["avg_n_vehicles_relocated"] = 0

				n_workers = 0
				tot_jobs = 0
				max_jobs = float('-inf')
				min_jobs = float('inf')
				for worker in sim.scooterRelocationStrategy.relocation_workers:
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
