from e3f2s.simulator.simulation.charging_primitives import *
import random


class ChargingStrategy(ChargingPrimitives):

	def get_charge_dict(self, vehicle, charge, booking_request, operator, charging_relocation_strategy):

		if self.simInput.sim_scenario_conf["battery_swap"]:

			charging_zone_id = booking_request["destination_id"]

			if self.simInput.sim_scenario_conf["time_estimation"]:

				if operator == "system":
					timeout_outward = np.random.exponential(
						self.simInput.sim_scenario_conf[
							"avg_reach_time"
						] * 60
					)
					charge["duration"] = np.random.exponential(
						self.simInput.sim_scenario_conf[
							"avg_service_time"
						] * 60
					)
					timeout_return = 0
					cr_soc_delta = 0
					resource = self.workers

				elif operator == "users":
					timeout_outward = 0
					timeout_return = 0
					cr_soc_delta = 0
					charge["duration"] = np.random.normal(
						self.simInput.sim_scenario_conf[
							"avg_service_time_users"
						] * 60,
						30 * 60
					)
					resource = self.workers

			else:

				timeout_outward = 0
				charge["duration"] = 0
				timeout_return = 0
				cr_soc_delta = 0
				resource = self.workers

		if self.simInput.sim_scenario_conf["distributed_cps"]:

			if charging_relocation_strategy == "closest_free":

				zones_by_distance = self.simInput.zones_cp_distances.loc[
					int(booking_request["destination_id"])
				].sort_values()

				free_pole_flag = 0
				# find the nearest available station with charging poles
				for zone in zones_by_distance.index:
					if self.charging_stations_dict[zone].charging_station.count < self.charging_stations_dict[
						zone].charging_station.capacity:
						free_pole_flag = 1
						charging_zone_id = zone
						cr_soc_delta = self.get_cr_soc_delta(
							booking_request["destination_id"],
							charging_zone_id,
							vehicle
						)
						if cr_soc_delta > booking_request["end_soc"]:
							free_pole_flag = 0
						else:
							charging_zone_id = charging_zone_id
							break

			elif charging_relocation_strategy == "random":
				zones_by_distance = self.simInput.zones_cp_distances.loc[int(booking_request["destination_id"])]
				free_pole_flag = 0

				# find a random station to charge
				while True:
					random_zone_id = random.choice(zones_by_distance.index)
					zones_by_distance.pop(random_zone_id)
					if self.charging_stations_dict[random_zone_id].charging_station.count < self.charging_stations_dict[
						random_zone_id].charging_station.capacity:
						free_pole_flag = 1
						charging_zone_id = random_zone_id
						cr_soc_delta = self.get_cr_soc_delta(booking_request["destination_id"], charging_zone_id)
						if cr_soc_delta > booking_request["end_soc"]:
							free_pole_flag = 0
						else:
							charging_zone_id = charging_zone_id
					if free_pole_flag == 1 or zones_by_distance.empty :
						break
			elif charging_relocation_strategy == 'closest_queueing':
				zones_by_distance = self.simInput.zones_cp_distances.loc[
					int(booking_request["destination_id"])
				].sort_values()

				free_pole_flag = 0
				for zone in zones_by_distance.index:
					free_pole_flag = 1
					charging_zone_id = zone
					cr_soc_delta = self.get_cr_soc_delta(
						booking_request["destination_id"], charging_zone_id, self.vehicles_list[vehicle]
					)
					if cr_soc_delta > booking_request["end_soc"]:
						free_pole_flag = 0
					else:
						charging_zone_id = charging_zone_id
						break

			else:
				print("No such charging relocation strategy supported")
				exit()

			if free_pole_flag == 0:
				charging_zone_id = self.simInput.closest_cp_zone[
					int(booking_request["destination_id"])
				]

			charging_station = self.charging_stations_dict[charging_zone_id].charging_station
			resource = charging_station

			if self.simInput.sim_scenario_conf["time_estimation"]:

				if operator == "system":

					timeout_outward = np.random.exponential(
						self.simInput.sim_scenario_conf[
							"avg_reach_time"
						] * 60
					)
					timeout_return = self.get_timeout(
						booking_request["destination_id"],
						charging_zone_id
					)

					charge["duration"] = vehicle.get_charging_time_from_perc(
						vehicle.soc.level,
						self.charging_stations_dict[charging_zone_id].flow_rate,
						self.simInput.sim_scenario_conf["profile_type"],
						charge["end_soc"]
					)

					cr_soc_delta = self.get_cr_soc_delta(
						booking_request["destination_id"], charging_zone_id, vehicle
					)
					charging_outward_distance = self.get_distance(booking_request["destination_id"], charging_zone_id)

					if cr_soc_delta > booking_request["end_soc"]:
						self.dead_vehicles.add(vehicle)
						self.n_dead_vehicles = len(self.dead_vehicles)
						self.sim_unfeasible_charge_bookings.append(booking_request)
					else:
						self.charging_return_distance += charging_outward_distance

				elif operator == "users":

					charging_zone_id = booking_request["destination_id"]
					charging_station = self.charging_stations_dict[charging_zone_id].charging_station
					resource = charging_station
					timeout_outward = 0
					charge["duration"] = self.vehicles_list[vehicle].get_charging_time_from_perc(
						self.vehicles_list[vehicle].soc.level,
						self.charging_stations_dict[charging_zone_id].flow_rate,
						self.simInput.sim_scenario_conf["profile_type"],
						charge["end_soc"]
					)
					timeout_return = 0
					cr_soc_delta = 0

			else:

				timeout_outward = 0
				charge["duration"] = 0
				timeout_return = 0
				cr_soc_delta = 0

		charge_dict = {
			"charge": charge,
			"resource": resource,
			"vehicle": vehicle,
			"operator": operator,
			"zone_id": charging_zone_id,
			"timeout_outward": timeout_outward,
			"timeout_return": timeout_return,
			"cr_soc_delta": cr_soc_delta
		}

		return charge_dict

	def check_charge(self, booking_request, vehicle):

		user_charge_flag = False

		if self.simInput.sim_scenario_conf["user_contribution"]:
			charge_flag, charge = self.check_user_charge(booking_request, vehicle)
			if charge_flag:
				user_charge_flag = True
				self.list_users_charging_bookings.append(booking_request)
				charge_dict = self.get_charge_dict(vehicle, charge, booking_request, "users")
				yield self.env.process(self.charge_vehicle(charge_dict))

			else:
				charge_flag, charge = self.check_system_charge(booking_request, vehicle)
				if charge_flag:
					self.list_system_charging_bookings.append(booking_request)
					charge_dict = self.get_charge_dict(vehicle, charge, booking_request, "system")
					yield self.env.process(self.charge_vehicle(charge_dict))
		else:
			charging_strategy = self.simInput.sim_scenario_conf["charging_strategy"]
			charge_flag, charge = self.check_system_charge(booking_request, vehicle, charging_strategy)
			if charge_flag:
				self.list_system_charging_bookings.append(booking_request)
				charging_relocation_strategy = self.simInput.sim_scenario_conf["charging_relocation_strategy"]
				charge_dict = self.get_charge_dict(
					vehicle, charge, booking_request, "system",
					charging_relocation_strategy
				)
				yield self.env.process(self.charge_vehicle(charge_dict))

		if charge_flag and not user_charge_flag:

			if not self.simInput.sim_scenario_conf["relocation"]:
				relocation_zone_id = charge_dict["zone_id"]

			elif self.simInput.sim_scenario_conf["relocation"]:
				relocation_zone_id = booking_request["destination_id"]

		else:

			relocation_zone_id = booking_request["destination_id"]

		return relocation_zone_id
