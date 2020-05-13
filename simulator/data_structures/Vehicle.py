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

        def booking(self, env, destination, duration_of_booking):
            if self.available:
                self._env = env
                self._zone.remove_vehicle(self)
                try:
                    self._available = False
                    yield self.env.timeout(duration_of_booking)
                except simpy.Interrupt:
                    #death! TODO
                self._soc  -= duration_of_booking*DISCHARGE_SPEED
                self._zone = destination
                self._zone.add_vehicle(self)
                if self._soc < ALPHA:
                   yield env.process(charge(station, self))
                else:
                    self._available = True

        @property
        def plate(self):
            return self._plate
        @plate.setter
        def plate(self, value):
            self._plate = value

        @property
        def zone(self):
            return self._plate
        @zone.setter
        def zone(self, value):
            self._zone = value

        @property
        def available(self):
            return self._available
        @available.setter
        def available(self, value):
            self._available = value

        @property
        def soc(self):
            return self._soc
        @soc.setter
        def soc(self, value):
            self._soc = value

        @property
        def battery_capacity(self):
            return self._battery_capacity
        @battery_capacity.setter
        def battery_capacity(self, value):
            self._battery_capacity = value

        @property
        def energy_efficiency(self):
            return self._energy_efficiency
        @energy_efficiency.setter
        def energy_efficiency(self, value):
            self._energy_efficiency = value

        @property
        def annual_leasing_cost(self):
            return self._annual_leasing_cost
        @annual_leasing_cost.setter
        def annual_leasing_cost(self, value):
            self._annual_leasing_cost = value

        @property
        def annual_insurance_cost(self):
            return self._annual_insurance_cost
        @annual_insurance_cost.setter
        def annual_insurance_cost(self, value):
            self._annual_insurance_cost = value

        @property
        def annual_mantenaince_cost(self):
            return self._annual_mantenaince_cost

        @annual_mantenaince_cost.setter
        def annual_mantenaince_cost(self, value):
            self._annual_mantenaince_cost = value


class Zone(object):
        def __init__(self, env, key, n_poles):
            self._env = env
            self._key = key
            self._n_poles = n_poles
            self.vehicles = []


        @property
        def n_poles(self):
            return self._n_poles
        @n_poles.setter
        def n_poles(self, value):
            self._n_poles = value

        def add_vehicle(self,v):
            self.vehicles.append(v)

        def remove_vehicle(self,v):
            self.vehicles.remove(v)

CHARGING_SPEED = 100

class Station(object):
        def __init__(self, env, num_poles, zone):
            self._env = env
            self._num_poles = num_poles
            self.pole = simpy.Resource(env)
            self.vehicles = []
            self._zone = zone

        def charge(self, car):
            start = self.env.now
            self.add_vehicle(car)
            try:
                yield self.env.timeout(car.soc*coefficientediricarica)
                car.soc = 100
            except simpy.Interrupt:
                # a customer takes the car before soc reaches 100
                car.soc += (self.env.now-start)*CHARGING_SPEED
            self.remove_vehicle(car)

        def add_vehicle(self,v):
            self.vehicles.append(v)

        def remove_vehicle(self,v):
            self.vehicles.remove(v)