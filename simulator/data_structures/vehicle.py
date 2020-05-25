import simpy
import random
import datetime


class Vehicle(object):

    def __init__(self, env, plate, start_zone, start_soc, vehicle_config, vehicle_cost_conf, sim_scenario_conf, sim_start_time):
        self.env = env
        self.plate = plate
        self.zone = start_zone
        self.available = True
        self.battery_capacity = vehicle_config["battery_capacity"]
        self.energy_efficiency = vehicle_config["energy_efficiency"]
        self.annual_leasing_cost = vehicle_cost_conf["annual_leasing_cost"]
        self.annual_insurance_cost = vehicle_cost_conf["annual_insurance_cost"]
        self.annual_mantenaince_cost = vehicle_cost_conf["annual_mantenaince_cost"]
        self.soc = simpy.Container(env, init=start_soc, capacity=100)
        self.alpha = sim_scenario_conf["alpha"]
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
        self.soc.get(abs(booking_request["soc_delta"]))
        yield self.env.timeout(booking_request["duration"])
        self.zone = booking_request["destination_id"]
        self.available = True
        self.current_status = {
            "time": booking_request["start_time"] + datetime.timedelta(seconds=booking_request['duration']),
            "status": "available",
            "soc": self.soc.level,
            "zone": booking_request["destination_id"]
        }
        self.status_dict_list.append(self.current_status)

