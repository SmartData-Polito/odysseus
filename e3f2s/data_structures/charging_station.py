example_station_config = {
	"voltage_output": 230,
	"current_output": 16,
	"fuel_type": "electric",
	"fuel_cost": 1.29
}

class Pole(object):
	def __init__(self, station_config):
		self.fuel_type = example_station_config["fuel_type"] #electric, gasoline, diesel, lpg, gnc
		self.fuel_cost = example_station_config["fuel_cost"]
		if self.fuel_type == "electric":
			self.voltage_output = example_station_config["voltage_output"]
			self.current_output= example_station_config["current_output"]
			self.flow_rate = self.voltage_output * self.current_output
		elif self.fuel_type in ["gasoline","diesel", "lpg","cng"]:
			#self.flow_rate = example_station_config["flow_rate"] #L/min, kg/min
			if self.fuel_type == "gasoline":
				self.energy_content = 32  # MJ/L
				self.flow_rate = 43.491
			elif self.fuel_type == "diesel":
				self.energy_content = 36  # MJ/L
				self.flow_rate = 43.491
			elif self.fuel_type == "lpg":
				self.energy_content = 24  # MJ/L
				self.flow_rate = 16.247
			elif self.fuel_type == "cng":
				self.energy_content = 44.4  # MJ/L
				self.flow_rate = 9.485

	def get_charging_time_from_energy(self,energy_mj): #energy in MegaJoules
		if self.fuel_type == "electric":
			energy_kwh = energy_mj / 3.6
			charging_time = (energy_kwh / self.flow_rate) * 3600
		elif self.fuel_type in ["gasoline", "diesel", "lpg", "cng"]:
			liters = energy_mj / self.energy_content
			charging_time = (liters / self.flow_rate) * 60
		return charging_time

	def get_energy_from_charging_time(self,charging_time): #charging_time in seconds
		if self.fuel_type == "electric":
			energy_kwh = self.flow_rate * (charging_time/3600)
			energy_mj = energy_kwh * 3.6
		elif self.fuel_type in ["gasoline", "diesel", "lpg", "cng"]:
			liters = self.flow_rate * (charging_time / 60)
			energy_mj = liters * self.energy_content
		return energy_mj

	def get_fuelcost_from_energy(self,energy_mj):
		if self.fuel_type == "electric":
			energy_kwh = energy_mj / 3.6
			return self.fuel_cost * energy_kwh
		elif self.fuel_type in ["gasoline", "diesel", "lpg", "cng"]:
			liters = energy_mj / self.energy_content
			return self.fuel_cost * liters

# a=Pole(example_station_config)
# print(a.get_energy_from_charging_time(15.119796755911661))
# print(a.get_charging_time_from_energy(55.64085206175491))
