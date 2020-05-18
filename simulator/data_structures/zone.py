class Zone(object):
    def __init__(self, env, key, n_poles):
        self._env = env
        self._key = key
        self._n_poles = n_poles
        self.vehicles = []


    def add_vehicle(self, v):
        self.vehicles.append(v)

    def remove_vehicle(self, v):
        self.vehicles.remove(v)