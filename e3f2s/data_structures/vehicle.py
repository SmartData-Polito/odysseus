import json
import requests
example_vehicle_config = {
	"vehicle_type": "car",
	"engine_type": "cng",
	"fuel_capacity": 11,
	"consumption": 34.48,
	"cost_car": 24700,
}
electric_production_emissions = requests.get('https://api.co2signal.com/v1/latest?countryCode=IT-NO',
                        headers={'auth-token': '658db0a8d45daedc'}) #North Italy code, see countries_api.json
class Vehicle(object):
	def __init__(self, vehicle_config):
		self.vehicle_type = vehicle_config["vehicle_type"] #car,scooter,
		self.engine_type = vehicle_config["engine_type"] #gasoline, diesel, lpg, gnc, electric
		self.consumption = vehicle_config["consumption"] #km/l, km/kWh
		self.capacity = vehicle_config["fuel_capacity"] #kWh (electric), Liter (gasoline,diesel,lpg), kilograms (gnc)
		self.cost_car = vehicle_config["cost_car"] # in €
		#self.current_percentage = 100

		if self.engine_type == "gasoline":
			self.welltotank_emission = 90.4 #gCO2eq/MJ
			self.energy_content = 32 #MJ/L
		elif self.engine_type == "diesel":
			self.welltotank_emission = 92.1 #gCO2eq/MJ
			self.energy_content = 36 #MJ/L
		elif self.engine_type == "lpg":
			self.welltotank_emission = 73.2 #gCO2eq/MJ
			self.energy_content = 24  # MJ/L
		elif self.engine_type == "cng":
			self.welltotank_emission = 67.6 #gCO2eq/MJ
			self.energy_content = 44.4  # MJ/kg
		elif self.engine_type == "electric":
			self.welltotank_emission = json.loads(electric_production_emissions.content)['data']['carbonIntensity'] #gCO2eq/Kwh


	def get_charging_time_from_perc(self, actual_level_perc, flow_amount, beta=100):
		# flow_amount is generalized to represent the amount of fuel
		# loaded in the vehicle per unit of time
		# electric: kW (3.3,7.4,11,22,43,50,120)
		# gasoline,diesel,lpg: liter/min (between 30-50)
		# gnc: kg/min (between 30-70)

		if self.engine_type == "electric":
			power_output = flow_amount / 1000
			capacity_left = ((beta - actual_level_perc) / 100) * self.capacity
			return (capacity_left / power_output) * 3600
		elif self.engine_type in ["gasoline", "diesel", "lpg","cng"]:
			flow_rate = flow_amount
			capacity_left = ((beta - actual_level_perc)/100) * self.capacity
			return (capacity_left/flow_rate) * 60

	def get_percentage_from_charging_time(self, charging_time, flow_amount):
		# flow_amount is generalized to represent the amount of fuel
		# loaded in the vehicle per unit of time
		# electric: kW (3.3,7.4,11,22,43,50,120)
		# gasoline,diesel,lpg: liter/min (between 30-50)
		# gnc: kg/min (between 30-70)

		if self.engine_type == "electric":
			power_output = flow_amount / 1000
			capacity_left = power_output * (charging_time / 3600)
			return 100 * (capacity_left / self.capacity)
		elif self.engine_type in ["gasoline", "diesel", "lpg", "cng"]:
			flow_rate = flow_amount
			capacity_left = (flow_rate * charging_time)/60
			return 100 * (capacity_left / self.capacity)

	def get_kwh_from_percentage(self, percentage):
		if self.engine_type == "electric":
			consumption_kwh = self.percentage_to_consumption(percentage)
			return consumption_kwh
		elif self.engine_type in ["gasoline", "diesel", "lpg", "cng"]:
			consumption_liter = self.percentage_to_consumption(percentage)
			return consumption_liter * self.energy_content * (1/3.6)

	def from_kml_to_lkm(self):
		return 1 / self.consumption

	def from_kml_to_energyperkm(self):
		perkm_consumption = self.from_kml_to_lkm()
		return perkm_consumption * self.energy_content

	def consumption_to_percentage(self, consumption):
		# x:100 = consumption : capacity
		percentage = (consumption * 100) / self.capacity
		return percentage

	def percentage_to_consumption(self, percentage):
		# x:100 = consumption : capacity
		consumption = (percentage * self.capacity) / 100
		return consumption

	def distance_to_consumption(self, distance):
		perkm_consumption = self.from_kml_to_lkm()
		tot_consumption = perkm_consumption * distance
		return tot_consumption

	def distance_to_emission(self, distance):
		if self.engine_type in ["gasoline", "diesel", "lpg", "cng"]:
			tot_emissions_perkm = self.welltotank_emission * self.from_kml_to_energyperkm()
			tot_emissions = distance * tot_emissions_perkm
			return tot_emissions
		elif self.engine_type == "electric":
			tot_emissions_perkm = self.welltotank_emission / self.consumption
			return distance * tot_emissions_perkm

# car = Vehicle(example_vehicle_config)
# distance = 130
# cons = car.distance_to_consumption(distance)
# print("Consumption = ", cons)
# print("Cons percentage = ", car.consumption_to_percentage(cons))
# print("Total emission Well to Wheel = ", car.distance_to_emission(distance))
# car.current_percentage -= car.consumption_to_percentage(cons)
# print(car.current_percentage)
# print("Charging time (s) = ",car.get_charging_time_from_perc(35,90))
# print("Charging perc = ", car.get_percentage_from_charging_time(15.119796755911661,35))

