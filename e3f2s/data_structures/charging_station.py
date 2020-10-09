#from e3f2s.data_structures.vehicle import Vehicle,example_vehicle_config


example_station_config = {
	#the speed of charging ,type : number
   "charging_speed":1,
   "number_of_poles": 100,
    #electric/gasoline
	"fuel_type": "electric"
}

class Charging_Station(object):
	def __init__(self, station_config):
		self.charging_speed = station_config["charging_speed"]
		self.number_of_poles = station_config["number_of_poles"]
		self.available_poles = self.number_of_poles

	def check_poles(self):
		if self.available_poles > 0 :
			return True
		else :
			return False

	def charging_one_vehicle(self, vehicle):
		if self.check_poles():
			self.available_poles -= 1
			return vehicle.charge(self.charging_speed)


	def finish_charging_vehicle (self, vehicle):
		self.available_poles += 1
		vehicle.charge_complete()


# v = Vehicle(example_vehicle_config)
# s = Charging_Station(example_station_config)
# distance = 20
# v.consume(distance)
# print(v.current_percentage)
# duration = s.charging_one_vehicle(v)
# print("duration:" , duration)
# #print(v.current_percentage)