import datetime

import simpy
from odysseus.supply_modelling.charging_station import Pole


class ChargingStation(Pole):

    def __init__(self, env, num_poles, zone_id, station_conf, sim_scenario_conf, sim_start_time):
        engine_type = sim_scenario_conf["engine_type"]
        if engine_type == "electric":
            profile_type = sim_scenario_conf["profile_type"]
            super().__init__(station_conf[engine_type][profile_type])
        else:
            super().__init__(station_conf[engine_type])
        self.env = env
        self.num_poles = num_poles
        self.charging_station = simpy.Resource(self.env, capacity=num_poles)
        self.zone_id = zone_id
        self.current_status = {
            "time": sim_start_time,
            "zone_id": self.zone_id,
            "queue": 0,
            "charging": 0
        }
        self.status_dict_list = [
            self.current_status
        ]

    def charge(self, vehicle, start_time, soc_delta_charging_trip, duration):
        vehicle.available = False
        if soc_delta_charging_trip > 0:
            vehicle.soc.get(soc_delta_charging_trip)
        with self.charging_station.request() as req:
            vehicle.zone = self.zone_id
            self.current_status = {
                "time": start_time,
                "zone_id": self.zone_id,
                "queue": len(self.charging_station.queue),
                "charging": self.charging_station.count
            }
            self.status_dict_list.append(self.current_status)
            vehicle.current_status = {
                "time": start_time,
                "status": "charging",
                "soc": vehicle.soc.level,
                "zone": self.zone_id
            }
            vehicle.status_dict_list.append(vehicle.current_status)
            yield req
            amount = vehicle.soc.capacity - vehicle.soc.level
            yield self.env.timeout(duration)
            vehicle.soc.put(amount)
        vehicle.available = True
        vehicle.current_status = {
            "time": start_time + datetime.timedelta(seconds=duration),
            "status": "available",
            "soc": vehicle.soc.level,
            "zone": self.zone_id
        }
        vehicle.status_dict_list.append(vehicle.current_status)

    def monitor(self, data, resource):
        data = resource.count + len(resource.queue)
