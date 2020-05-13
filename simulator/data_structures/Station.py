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