class Zone(object):

    def __init__(self, env, zone_id, sim_start_time, vehicles):
        self.env = env
        self.zone_id = zone_id
        self.vehicles = vehicles
        self.current_status = dict()
        self.status_dict_list = list()
        self.update_status(sim_start_time)

    def update_status(self, t):

        self.current_status = {
            "t": t,
            "vehicles_parked": len(self.vehicles),
        }
        self.status_dict_list.append(self.current_status)

    def add_vehicle(self, t):
        self.update_status(t)

    def remove_vehicle(self, t):
        self.update_status(t)
