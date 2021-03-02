import simpy
import random
import datetime
from e3f2s.supply_modelling.vehicle import Vehicle as Vehicle_definition

class Vehicle(Vehicle_definition):

    def __init__(self, env, plate, start_zone, start_soc,
                 vehicle_config, energymix_conf, sim_scenario_conf, sim_start_time):

        engine_type = sim_scenario_conf["engine_type"]
        model = sim_scenario_conf["vehicle_model_name"]
        if engine_type == "electric":
            energymix = energymix_conf
        else:
            energymix = {}
        super().__init__(vehicle_config[engine_type][model], energymix)

        self.env = env
        self.plate = plate
        self.zone = start_zone
        #self.alpha = sim_scenario_conf["alpha"]

        #self.battery_capacity = vehicle_config["battery_capacity"]
        #self.energy_efficiency = vehicle_config["energy_efficiency"]

        self.available = True
        self.soc = simpy.Container(env, init=start_soc, capacity=100)
        self.current_status = {
            "time": sim_start_time,
            "status": "available",
            "soc": self.soc.level,
            "zone": self.zone
        }
        self.status_dict_list = [
            self.current_status
        ]

    def booking(self, booking_request):

        self.available = False
        self.current_status = {
            "time": booking_request["start_time"],
            "status": "booked",
            "soc": self.soc.level,
            "zone": self.zone
        }
        self.status_dict_list.append(self.current_status)
        yield self.env.timeout(booking_request["duration"])
        fuel_consumed = self.distance_to_consumption(booking_request["driving_distance"]/1000)
        percentage = self.consumption_to_percentage(fuel_consumed)
        self.soc.get(percentage)
        self.zone = booking_request["destination_id"]
        self.available = True
        self.current_status = {
            "time": booking_request["start_time"] + datetime.timedelta(seconds=booking_request['duration']),
            "status": "available",
            "soc": self.soc.level,
            "zone": booking_request["destination_id"]
        }
        self.status_dict_list.append(self.current_status)

    def charge(self, percentage):
        self.soc.put(percentage)
