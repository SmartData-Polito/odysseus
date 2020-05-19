import simpy
import random


class Vehicle(object):

    def __init__(self, env, plate, zone, vehicle_config, vehicle_cost_conf, sim_scenario_conf):
        self.env = env
        self.plate = plate
        self.zone = zone
        zone.add_vehicle(self)
        self.available = True
        self.battery_capacity = vehicle_config.battery_capacity
        self.energy_efficiency = vehicle_config.energy_efficiency
        self.annual_leasing_cost = vehicle_cost_conf.annual_leasing_cost
        self.annual_insurance_cost = vehicle_cost_conf.annual_insurance_cost
        self.annual_mantenaince_cost = vehicle_cost_conf.annual_mantenaince_cost
        self.soc = simpy.Container(env, init=random.randint(50, 100), capacity=100)
        # self.mon_proc = env.process(self.monitor_soc())
        self.alpha = sim_scenario_conf["alpha"]
        self.current_status = {"start_time": env.now, "status": "available",
                               "start_soc": self.alpha, "zone": self._zone}
        self.status_dict_list = [
            self.current_status
        ]

    # def charging_trip(self, station_dest):
    # yield --> supponiamo subito! oppure TODO
    # self._zone.remove_vehicle(vehicle)
    # try:
    # yield env.timeout(15)  # il tempo che ci vuole a raggiungere una station ??
    # except simpy.Interrupt:
    # yield env.timeout(45)  # CHARGE DEATH - 45 = 30 per far venire il carro attrezzi + 15 per raggiungere il pole
    # station_dest.env.process(charge(self))

    def booking(self, booking_request):
        if self.available:
            self.zone.remove_vehicle(self._plate)
            self.available = False
            self.current_status = {"time": env.now, "status": "available", "soc": self.alpha,
                                   "zone": self.zone}
            self.status_dict_list.append(self.current_status)
            yield vehicle.soc.get(booking_request["soc_delta"])
            yield self.env.timeout(booking_request["duration"] * 60)
            self.zone = zone[booking_request["destination_id"]]
            self.current_status = {"time": env.now, "status": "available", "soc": self.alpha,
                                   "zone": self.zone}
            self.status_dict_list.append(self.current_status)
            # if self.soc.level < self.alpha:
            # yield env.process(charging_trip(self, station_dest))
            # else:
            # self.available = True
