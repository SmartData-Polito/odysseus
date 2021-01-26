from math import sqrt
class Pole(object):
	def __init__(self, station_config):
		self.fuel_type = station_config["fuel_type"] #electric, gasoline, diesel, lpg, gnc
		#self.fuel_cost = station_config["fuel_cost"]
		if self.fuel_type == "electric":
			self.voltage_output = station_config["voltage_output"]
			self.current_output= station_config["current_output"]
			self.profile_type = station_config["profile_type"]
			if self.profile_type in ["wall_plug","single_phase_1","single_phase_2","dcfc_1","dcfc_2"]:
				self.flow_rate = self.voltage_output * self.current_output
			elif self.profile_type in ["three_phase_1","three_phase_2","three_phase_3"]:
				self.flow_rate = self.voltage_output * self.current_output * sqrt(3)
			# self.cost = station_config["cost"]
		elif self.fuel_type in ["gasoline","diesel", "lpg","cng"]:
			#self.flow_rate = example_station_config["flow_rate"] #L/min, kg/min
			if self.fuel_type == "gasoline": #GASOLINE E5
				self.lower_heating_value = 42.3 #MJ/kg
				self.density = 745.8  # g/L
				self.flow_rate = 43.491
			elif self.fuel_type == "diesel": #DIESEL B7
				self.lower_heating_value = 42.7  # MJ/kg
				self.density = 836.1  # g/L
				self.flow_rate = 43.491
			elif self.fuel_type == "lpg":
				self.lower_heating_value = 46  # MJ/kg
				self.density = 550  # g/L
				self.flow_rate = 16.247
			elif self.fuel_type == "cng":
				self.lower_heating_value = 48  # MJ/kg
				self.density = 1000  # g/kg
				self.flow_rate = 9.485

	def get_charging_time_from_energy(self,energy_mj): #energy in MegaJoules
		if self.fuel_type == "electric":
			energy_kwh = energy_mj / 3.6
			charging_time = (energy_kwh / self.flow_rate) * 3600
		elif self.fuel_type in ["gasoline", "diesel", "lpg", "cng"]:
			liters = energy_mj / (
					self.lower_heating_value / (1 / (self.density / 1000)) # converted lhv from MJ/kg to MJ/L
			)
			charging_time = (liters / self.flow_rate) * 60
		return charging_time

	def get_energy_from_charging_time(self,charging_time): #charging_time in seconds
		if self.fuel_type == "electric":
			energy_kwh = self.flow_rate * (charging_time/3600)
			energy_mj = energy_kwh * 3.6
		elif self.fuel_type in ["gasoline", "diesel", "lpg", "cng"]:
			liters = self.flow_rate * (charging_time / 60)
			energy_mj = liters * (
					self.lower_heating_value / (1 / (self.density / 1000)) # converted lhv from MJ/kg to MJ/L
			)
		return energy_mj

	def get_fuelcost_from_energy(self,energy_mj):
		if self.fuel_type == "electric":
			energy_kwh = energy_mj / 3.6
			return self.fuel_cost * energy_kwh
		elif self.fuel_type in ["gasoline", "diesel", "lpg", "cng"]:
			liters = energy_mj / (
					self.lower_heating_value / (1 / (self.density / 1000)) # converted lhv from MJ/kg to MJ/L
			)
			return self.fuel_cost * liters

# a=Pole(example_station_config)
# print(a.get_energy_from_charging_time(15.119796755911661))
# print(a.get_charging_time_from_energy(55.64085206175491))
