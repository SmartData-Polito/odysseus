import simpy
import random

DISCHARGE_SPEED = 100

class Vehicle(object):

        def __init__(self, env, plate, zone, vehicle_config, vehicle_cost_conf, sim_scenario_conf):
            self._env = env
            self._plate = plate
            self._zone = zone
            zone.add_vehicle(self)
            self._available = True
            self._battery_capacity = vehicle_config.battery_capacity
            self._energy_efficiency = vehicle_config.energy_efficiency
            self._annual_leasing_cost = vehicle_cost_conf.annual_leasing_cost
            self._annual_insurance_cost = vehicle_cost_conf.annual_insurance_cost
            self._annual_mantenaince_cost = vehicle_cost_conf.annual_mantenaince_cost
            self._soc = simpy.Container(env, init = random.randint(50,100), capacity=100)
            self.mon_proc = env.process(self.monitor_soc())
            self.alpha = sim_scenario_conf["alpha"]
            self.status = [
                {"start_time": env.now, "end_time": env.now, "status":"available", "start_soc": self.alpha, "zone": self._zone}
            ]

        def monitor_soc(self):

            while True:
                if self._soc.level < ALPHA:
                    env.process(charging_trip(env, self))

        def charging_trip(vehicle, station_dest):
            #yield --> supponiamo subito! oppure TODO
            self._zone.remove_vehicle(vehicle)
            try:
                yield env.timeout(15) # il tempo che ci vuole a raggiungere una station ??
            except simpy.Interrupt:
                yield env.timeout(45) # CHARGE DEATH - 45 = 30 per far venire il carro attrezzi + 15 per raggiungere il pole
            station_dest.env.process(charge(env, self))

        def booking(self, booking_request):
            request = resource.request()
            if self.available:
                self._zone.remove_vehicle(self)
                self._available = False
                change_status(self, status[-1].get("end_time"), env.now(), "available", self._soc)
                start_soc = self._soc
                yield vehicle._soc.get(booking_request["soc_delta"])
                yield self.env.timeout(booking_request["duration"])
                self._zone = zone[booking_request["destination_id"]]
                self._zone.add_vehicle(self)
                change_status(self, status[-1].get("end_time"), env.now(), "booked", start_soc)
                if self._soc < self.alpha:
                   yield env.process(charging_trip(env, self, station_dest))
                else:
                    self._available = True


        def change_status(self, start_time, end_time, status, start_soc):
            dict = {"start_time": start_time, "end_time": end_time, "status": status, "start_soc": start_soc, "end_soc": self._soc, "zone": self._zone}
            self.status.append(dict)