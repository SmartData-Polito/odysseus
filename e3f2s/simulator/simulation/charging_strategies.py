from e3f2s.simulator.simulation.charging_primitives import *


class ChargingStrategy (ChargingPrimitives):

	def get_charge_dict(self, vehicle, charge, booking_request, operator):

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
					charge["duration"] = np.random.exponential(
						240 * 60
					)
					resource = self.workers

			else:

				timeout_outward = 0
				charge["duration"] = 0
				timeout_return = 0
				cr_soc_delta = 0
				resource = self.workers

		if self.simInput.sim_scenario_conf["hub"]:

			charging_zone_id = self.simInput.hub_zone
			resource = self.charging_hub

			if self.simInput.sim_scenario_conf["time_estimation"]:

				timeout_outward = self.get_timeout(
					booking_request["destination_id"],
					charging_zone_id
				)
				charge["duration"] = get_charging_time(
					charge["soc_delta"]
				)
				if not self.simInput.sim_scenario_conf["relocation"]:
					timeout_return = 0
				elif self.simInput.sim_scenario_conf["relocation"]:
					timeout_return = timeout_outward

				cr_soc_delta = self.get_cr_soc_delta(
					booking_request["destination_id"],
					charging_zone_id
				)

				if cr_soc_delta > booking_request["end_soc"]:
					self.dead_vehicles.add(vehicle)
					self.n_dead_vehicles = len(self.dead_vehicles)
					self.sim_unfeasible_charge_bookings.append(booking_request)

			else:

				timeout_outward = 0
				charge["duration"] = 0
				timeout_return = 0
				cr_soc_delta = 0

		if self.simInput.sim_scenario_conf["distributed_cps"]:

			zones_by_distance = self.simInput.zones_cp_distances.loc[
				int(booking_request["destination_id"])
			].sort_values()

			free_pole_flag = 0
			for zone in zones_by_distance.index:
				if self.charging_stations_dict[zone].charging_station.count < self.charging_stations_dict[zone].charging_station.capacity:
					free_pole_flag = 1
					charging_zone_id = zone
					cr_soc_delta = self.get_cr_soc_delta(booking_request["destination_id"], charging_zone_id)
					if cr_soc_delta > booking_request["end_soc"]:
						free_pole_flag = 0
					else:
						charging_zone_id_ = charging_zone_id
						break

			if free_pole_flag == 0:
				charging_zone_id = self.simInput.closest_cp_zone[
					int(booking_request["destination_id"])
				]

			with open("check_file.csv", "a") as f:
				f.write(",".join([str(booking_request["destination_id"]), str(charging_zone_id), str(free_pole_flag)]) + "\n")

			charging_station = self.charging_stations_dict[zone].charging_station
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
					charge["duration"] = get_charging_time(
						charge["soc_delta"]
					)
					cr_soc_delta = self.get_cr_soc_delta(booking_request["destination_id"], charging_zone_id)

					if cr_soc_delta > booking_request["end_soc"]:
						self.dead_vehicles.add(vehicle)
						self.n_dead_vehicles = len(self.dead_vehicles)
						self.sim_unfeasible_charge_bookings.append(booking_request)

				elif operator == "users":

					charging_zone_id = booking_request["destination_id"]
					charging_station = self.charging_poles_dict[charging_zone_id]
					resource = charging_station
					timeout_outward = 0
					charge["duration"] = get_charging_time(
						charge["soc_delta"]
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

	def check_charge (self, booking_request, vehicle):

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
			charge_flag, charge = self.check_system_charge(booking_request, vehicle)
			if charge_flag:
				self.list_system_charging_bookings.append(booking_request)
				charge_dict = self.get_charge_dict(vehicle, charge, booking_request, "system")
				yield self.env.process(self.charge_vehicle(charge_dict))

		if charge_flag and not user_charge_flag:

			if not self.simInput.sim_scenario_conf["relocation"]:
				relocation_zone_id = charge_dict["zone_id"]

			elif self.simInput.sim_scenario_conf["relocation"]:
				relocation_zone_id = booking_request["destination_id"]

		else:

			relocation_zone_id = booking_request["destination_id"]

		return relocation_zone_id
