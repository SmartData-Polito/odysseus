example_vehicle_config = {
    "vehicle_type": "car",
    "engine_type": "gasoline",
    "capacity": 60,
    "consumption": 1,
    "emissions": 90, #gr/Km CO2
}
# add comments
example_single_run_conf={
    "beta": 100
}
class Vehicle:
    def __init__(self, vehicle_config):

        self.vehicle_type = vehicle_config["vehicle_type"]
        self.engine_type = vehicle_config["engine_type"]
        self.consumption = vehicle_config["consumption"]
        self.capacity = vehicle_config["capacity"]
        self.emissions = vehicle_config["emissions"]
        self.current_percentage = 100
        self.status = "available"

    def distance_to_consumption(self, distance):
        #Distance in km, volumes in liters, energy in kWh
        tot_consumption = self.consumption * distance
        return tot_consumption

    def consumption_to_percentage(self, consumption):
        # x:100 = consumption : capacity
        percentage = (consumption * 100) / self.capacity
        return percentage

    def distance_to_emission(self, distance):
        tot_emissions = distance * self.emissions
        return tot_emissions

    def consume(self, distance):
        tot_consumption = self.distance_to_consumption(distance)
        consume_percentage = self.consumption_to_percentage(tot_consumption)
        self.current_percentage = self.current_percentage - consume_percentage

    #return charging time of the vehicle
    def charge(self,charging_speed):
        self.status = "charging"
        if charging_speed :
            charging_duration =  ( self.capacity *( example_single_run_conf["beta"]- self.current_percentage )/100) / charging_speed

        else :
            charging_duration = 0
        self.current_percentage = example_single_run_conf["beta"]
        return charging_duration

    def charge_complete(self):
        self.status = "available"


