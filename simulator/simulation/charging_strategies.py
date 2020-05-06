import numpy as np

from simulator.simulation.charging_primitives import EFFCS_ChargingPrimitives


class EFFCS_ChargingStrategy (EFFCS_ChargingPrimitives):

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
