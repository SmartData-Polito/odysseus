import datetime

import simpy
from simulator.simulation.charging_primitives import get_charging_time


class Station(object):

    def __init__(self, env, num_poles, zone):
        self.env = env
        self.charging_station = simpy.Resource(self.env, num_poles)
        self.zone = zone

    def charge(self, vehicle, start_time):
        with self.charging_station.request() as req:
            vehicle.zone = self.zone
            vehicle.current_status = {
                "time": start_time,
                "status": "charging",
                "soc": vehicle.soc.level,
                "zone": self.zone
            }
            vehicle.status_dict_list.append(vehicle.current_status)
            yield req
            amount = vehicle.soc.capacity - vehicle.soc.level
            yield self.env.timeout(get_charging_time(amount))
            vehicle.soc.put(amount)
        vehicle.available = True
        vehicle.current_status = {
            "time": start_time + datetime.timedelta(seconds=get_charging_time(amount)),
            "status": "charging",
            "soc": vehicle.soc.level,
            "zone": self.zone
        }
        vehicle.status_dict_list.append(vehicle.current_status)
