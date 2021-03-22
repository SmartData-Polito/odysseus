from odysseus.simulator.simulation.relocation_primitives import *
import random


class RelocationStrategy(RelocationPrimitives):

	def get_relocate_dict(self, vehicle, relocate, charging_request, operator, post_relocation_strategy):

		if self.simInput.supply_model_conf["distributed_cps"]:

			if post_relocation_strategy == "random_post_relocation":
				# zones_by_distance = self.simInput.zones_cp_distances.loc[int(charging_request["destination_id"])]
				relocate_zones_list = self.simInput.valid_zones

				free_zone_flag = 0

				# find a random zone to relocate
				while True:
					random_zone_id = random.choice(relocate_zones_list)
					print("random_zone_id:" + random_zone_id)
					# remove the element
					relocate_zones_list.pop(random_zone_id)
					# if self.charging_stations_dict[random_zone_id].charging_station.count < self.charging_stations_dict[
					# 	random_zone_id].charging_station.capacity:
					free_zone_flag = 1
					relocation_zone_id = random_zone_id
					cr_soc_delta = self.get_cr_soc_delta(charging_request["destination_id"], relocation_zone_id)
					#no enough energy to do post relocation
					if cr_soc_delta > charging_request["end_soc"]:
						free_zone_flag = 0
					else:
						relocation_zone_id = relocation_zone_id
					if free_zone_flag == 1 or relocate_zones_list.empty:
						# print("end of choosing")
						break

			if free_zone_flag == 0:
				print("No satisfied zone to relocate")
				relocation_flag = 0

			#relocation_station = self.charging_stations_dict[charging_zone_id].charging_station
			#resource = relocation_station

			if self.simInput.supply_model_conf["time_estimation"]:

				if operator == "system":

					# timeout_outward = np.random.exponential(
					# 	self.simInput.sim_scenario_conf[
					# 		"avg_reach_time"
					# 	] * 60
					# )
					timeout_return = self.get_timeout(
						charging_request["destination_id"],
						relocation_zone_id
					)
					relocate["duration"] = 0
					cr_soc_delta = self.get_cr_soc_delta(charging_request["destination_id"], relocation_zone_id)

					if cr_soc_delta > charging_request["end_soc"]:
						self.dead_vehicles.add(vehicle)
						self.n_dead_vehicles = len(self.dead_vehicles)
						self.sim_unfeasible_relocate_chargings.append(charging_request)

			else:

				#timeout_outward = 0
				relocate["duration"] = 0
				timeout_return = 0
				cr_soc_delta = 0

		relocate_dict = {
			"relocate": relocate,
			#"resource": resource,
			"vehicle": vehicle,
			"operator": operator,
			"zone_id": relocation_zone_id,
			#"timeout_outward": timeout_outward,
			"timeout_return": timeout_return,
			"cr_soc_delta": cr_soc_delta
		}

		return relocate_dict

	def check_relocate(self, charging_request, vehicle):

		# user_charge_flag = False

		# if self.simInput.sim_scenario_conf["user_contribution"]:
		# 	charge_flag, charge = self.check_user_charge(booking_request, vehicle)
		# 	if charge_flag:
		# 		user_charge_flag = True
		# 		self.list_users_charging_bookings.append(booking_request)
		# 		charge_dict = self.get_charge_dict(vehicle, charge, booking_request, "users")
		# 		yield self.env.process(self.charge_vehicle(charge_dict))
		#
		# 	else:
		# 		charge_flag, charge = self.check_system_charge(booking_request, vehicle)
		# 		if charge_flag:
		# 			self.list_system_charging_bookings.append(booking_request)
		# 			charge_dict = self.get_charge_dict(vehicle, charge, booking_request, "system")
		# 			yield self.env.process(self.charge_vehicle(charge_dict))

		relocate_flag, relocate = self.check_system_relocate(charging_request, vehicle)
		if relocate_flag:
			self.list_system_relocation_bookings.append(charging_request)
			post_relocation_strategy = self.simInput.supply_model_conf["post_relocation_strategy"]
			relocate_dict = self.get_relocate_dict(vehicle, relocate, charging_request, "system",
												post_relocation_strategy)
			yield self.env.process(self.relocate_vehicle(relocate_dict))

		# if relocate_flag and not user_charge_flag:
		#
		# 	if not self.simInput.sim_scenario_conf["relocation"]:
		# 		relocation_zone_id = charge_dict["zone_id"]
		#
		# 	elif self.simInput.sim_scenario_conf["relocation"]:
		# 		relocation_zone_id = booking_request["destination_id"]
		# 		#No enough battery
		else:

			relocation_zone_id = charging_request["destination_id"]

		return relocation_zone_id
