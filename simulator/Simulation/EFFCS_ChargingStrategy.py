
import numpy as np

from simulator.Simulation.EFFCS_ChargingPrimitives import EFFCS_ChargingPrimitives


class EFFCS_ChargingStrategy (EFFCS_ChargingPrimitives):

	def check_charge (self, booking_request, vehicle):

		charge_flag = False
		user_charge_flag = False

		if self.simInput.sim_scenario_conf["battery_swap"]:

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
						unfeasible_charge_flag = False
						charge_dict = self.get_charge_dict(vehicle, charge, booking_request, "system")
						yield self.env.process(self.charge_vehicle(charge_dict))

			else:

				charge_flag, charge = self.check_system_charge(booking_request, vehicle)
				if charge_flag:
					self.list_system_charging_bookings.append(booking_request)
					unfeasible_charge_flag = False
					charge_dict = self.get_charge_dict(vehicle, charge, booking_request, "system")
					yield self.env.process(self.charge_vehicle(charge_dict))

		elif self.simInput.sim_scenario_conf["user_contribution"]:

			charge_flag, charge = self.check_user_charge(booking_request, vehicle)
			if charge_flag and booking_request["destination_id"] in self.charging_poles_dict.keys():
				user_charge_flag = True
				self.list_users_charging_bookings.append(booking_request)
				charging_zone_id = \
					booking_request["destination_id"]
				charging_station = \
					self.charging_poles_dict[charging_zone_id]
				relocation_zone_id = booking_request["destination_id"]
				timeout_outward = 0
				timeout_return = 0
				cr_soc_delta = 0

				yield self.env.process(
					self.charge_vehicle(
						charge,
						charging_station,
						vehicle,
						"users",
						charging_zone_id,
						timeout_outward,
						timeout_return,
						cr_soc_delta
					)
				)

			else:

				charge_flag, charge = \
					self.check_system_charge(booking_request, vehicle)

				if charge_flag:

					self.list_system_charging_bookings\
						+= [booking_request]

					if self.simInput.sim_scenario_conf["hub"]:

						unfeasible_charge_flag, \
						charging_zone_id, \
						timeout_outward, \
						timeout_return, \
						cr_soc_delta = \
							self.compute_hub_charging_params(booking_request, vehicle)


						yield self.env.process\
						   (self.charge_vehicle\
							(charge,
							 self.charging_hub,
							 vehicle,
							 "system",
							 charging_zone_id,
							 timeout_outward,
							 timeout_return,
							 cr_soc_delta))

					if self.simInput.sim_scenario_conf["distributed_cps"]\
					and self.simInput.sim_scenario_conf["system_cps"]:

						self.list_system_charging_bookings\
							+= [booking_request]

						unfeasible_charge_flag, \
						charging_station, \
						charging_zone_id, \
						timeout_outward, \
						timeout_return, \
						cr_soc_delta = \
							self.compute_cp_charging_params(booking_request, vehicle)

						yield self.env.process\
						   (self.charge_vehicle\
							(charge,
							 charging_station,
							 vehicle,
							 "system",
							 charging_zone_id,
							 timeout_outward,
							 timeout_return,
							 cr_soc_delta))

		elif not self.simInput.sim_scenario_conf["user_contribution"]:

			charge_flag, charge = \
				self.check_system_charge(booking_request, vehicle)

			if charge_flag:

				self.list_system_charging_bookings\
					+= [booking_request]

				if self.simInput.sim_scenario_conf["hub"]:

					unfeasible_charge_flag, \
					charging_zone_id, \
					timeout_outward, \
					timeout_return, \
					cr_soc_delta = \
						self.compute_hub_charging_params(booking_request, vehicle)

					yield self.env.process\
					   (self.charge_vehicle\
						(charge,
						 self.charging_hub,
						 vehicle,
						 "system",
						 charging_zone_id,
						 timeout_outward,
						 timeout_return,
						 cr_soc_delta))

				if self.simInput.sim_scenario_conf["distributed_cps"]\
				and self.simInput.sim_scenario_conf["system_cps"]:

					unfeasible_charge_flag, \
					charging_station, \
					charging_zone_id, \
					timeout_outward, \
					timeout_return, \
					cr_soc_delta = \
						self.compute_cp_charging_params(booking_request, vehicle)

					yield self.env.process\
					   (self.charge_vehicle\
						(charge,
						 charging_station,
						 vehicle,
						 "system",
						 charging_zone_id,
						 timeout_outward,
						 timeout_return,
						 cr_soc_delta))

		# Post-charging relocation

		if charge_flag and not user_charge_flag:

			if not self.simInput.sim_scenario_conf["relocation"]:
				relocation_zone_id = charge_dict["zone_id"]

			elif self.simInput.sim_scenario_conf["relocation"]:
				relocation_zone_id = booking_request["destination_id"]

		else:

			relocation_zone_id = booking_request["destination_id"]

		return relocation_zone_id
