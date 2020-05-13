import simpy
import random

DISCHARGE_SPEED = 100
ALPHA = 25
class Vehicle(object):

        def __init__(self, env, plate, zone, vehicle_config, vehicle_cost_conf):
            self._env = env
            self._plate = plate
            self._zone = zone
            zone.add_vehicle(self)
            self._available = True
            self._soc = random.randint(*100)
            self._battery_capacity = vehicle_config.battery_capacity
            self._energy_efficiency = vehicle_config.energy_efficiency
            self._annual_leasing_cost = vehicle_cost_conf.annual_leasing_cost
            self._annual_insurance_cost = vehicle_cost_conf.annual_insurance_cost
            self._annual_mantenaince_cost = vehicle_cost_conf.annual_mantenaince_cost

        def booking(self, env, booking_request, destination):
            if self.available:
                self._env = env
                self._zone.remove_vehicle(self)
                try:
                    self._available = False
                    yield self.env.timeout(booking_request["duration"])
                except simpy.Interrupt:
                    #death! TODO
                self._soc -= booking_request["start_soc"] + booking_request["soc_delta"]
                self._zone = zone[booking_request["destination_id"]]
                self._zone.add_vehicle(self)
                if self._soc < ALPHA:
                   yield env.process(charge(station, self))
                else:
                    self._available = True
