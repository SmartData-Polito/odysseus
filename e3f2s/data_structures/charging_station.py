example_station_config = {
	"voltage_output": 230,
	"current_output": 16,
	"flow_rate": 35,
	"fuel_type": "electric",
	"fuel_cost": 1.29
}

class Charging_Pole(object):
	def __init__(self, station_config):
		self.fuel_type = example_station_config["fuel_type"] #electric, gasoline, diesel, lpg, gnc
		self.fuel_cost = example_station_config["fuel_cost"]
		if self.fuel_type == "electric":
			self.voltage_output = example_station_config["voltage_output"]
			self.current_output= example_station_config["current_output"]
			self.rated_power = self.voltage_output * self.current_output
		elif self.fuel_type in ["gasoline","diesel", "lpg","gnc"]:
			self.flow_rate = example_station_config["flow_rate"] #L/min, kg/min

	def get_charging_time_from_energy(self,energy):
		if self.fuel_type == "electric":
			return (energy/self.rated_power)*3600
		else:
			print("The pole must be electric")
	def get_energy_from_charging_time(self,charging_time):
		if self.fuel_type == "electric":
			return self.rated_power*(charging_time/3600)
		else:
			print("The pole must be electric")
	def get_charging_time_from_liters(self,liters):
		if self.fuel_type in ["gasoline","diesel", "lpg","gnc"]:
			return (liters/self.flow_rate)*60
		else:
			print("The pole must not be electric")
	def get_liters_from_charging_time(self,charging_time):
		if self.fuel_type in ["gasoline","diesel", "lpg","gnc"]:
			return (self.flow_rate*(charging_time/60))
		else:
			print("The pole must not be electric")

	def get_fuelcost_per_amount(self,fuel_amount):
		return self.fuel_cost * fuel_amount

a=Charging_Pole(example_station_config)
print(a.get_charging_time_from_energy(23*3600000))
print(a.get_energy_from_charging_time(1))

