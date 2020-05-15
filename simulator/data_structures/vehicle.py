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
            self._soc = simpy.Container(env, init = random.randint(*100), capacity=100)
            self.mon_proc = env.process(self.monitor_soc(env))
            self.alpha = sim_scenario_conf["alpha"]


        def monitor_soc(self, env):
            while True:
                if self._soc.level < ALPHA:
                    print(f'Starting relocation to charging pole at {env.now}')
                    env.process(charging_trip(env, self))

        def charging_trip(env, vehicle, station_dest):
            #yield --> supponiamo subito! oppure TODO
            print(f'Charging trip starting at {env.now} ')
            self._zone.remove_vehicle(vehicle)
            try:
                yield env.timeout(15) # il tempo che ci vuole a raggiungere una station ??
            except simpy.Interrupt:
                yield env.timeout(45) # CHARGE DEATH - 45 = 30 per far venire il carro attrezzi + 15 per raggiungere il pole
            station_dest.env.process(charging(env, self))

        def booking(self, env, booking_request):
            request = resource.request()
            if self.available:
                self._env = env
                self._zone.remove_vehicle(self)
                try:
                    self._available = False
                    yield vehicle._soc.get(booking_request["soc_delta"])
                    yield self.env.timeout(booking_request["duration"])
                except simpy.Interrupt:
                    yield self.env.timeout(30) #30 min per far venire il carro attrezzi, DEATH TODO
                self._zone = zone[booking_request["destination_id"]]
                self._zone.add_vehicle(self)
                if self._soc < self.alpha:
                   yield env.process(charging_trip(env, self, station_dest))
                else:
                    self._available = True
