import simpy
from simulator.Simulation.charging_primitives import get_charging_time


class Station(object):

    def __init__(self, env, num_poles, zone):
        self.env = env
        self.charging_station = simpy.Resource(env, num_poles)
        self.zone = zone

    def charge(self, vehicle):
        with self.charging_station.request() as req:
            vehicle.zone = charging_station.zone
            vehicle.current_status = {"time": env.now, "status": "charging",
                                      "soc": vehicle.soc.level, "zone": self.zone}
            vehicle.status_dict_list.append(vehicle.current_status)
            yield req
            amount = vehicle.soc.capacity - vehicle.soc.level
            yield self.env.timeout(get_charging_time(amount))  # devo mettere amount o level ?
            vehicle.soc.put(amount)
            resource.release(request)
            vehicle.available = True
            vehicle.current_status = {"time": env.now, "status": "charging",
                                      "soc": vehicle.soc.level, "zone": self.zone}
            vehicle.status_dict_list.append(vehicle.current_status)
