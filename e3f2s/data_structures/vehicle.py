example_vehicle_config = {
    "vehicle_type": "car",
    "engine_type": "gasoline",
    "capacity": 60,
    "consumption": 1,
    "emissions": 90, #gr/Km CO2
}
# add comments
class Vehicle:
    def __init__(self, vehicle_config):

        self.vehicle_type = vehicle_config["vehicle_type"]
        self.engine_type = vehicle_config["engine_type"]
        self.consumption = vehicle_config["consumption"]
        self.capacity = vehicle_config["capacity"]
        self.emissions = vehicle_config["emissions"]
        self.current_percentage = 100

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
