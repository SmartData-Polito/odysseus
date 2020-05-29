class Zone(object):

    def __init__(self, env, zone_id, sim_start_time):
        self.env = env
        self.zone_id = zone_id
        self.vehicles = []
        self.current_status = {
            "t": sim_start_time,
            "vehicles_parked": 0,
        }
        self.status_dict_list = [
            self.current_status
        ]

    def add_vehicle(self, t):
        self.current_status = {
            "t": t,
            "vehicles_parked": self.current_status["vehicles_parked"] + 1,
        }
        self.status_dict_list.append(self.current_status)

    def remove_vehicle(self, t):
        self.current_status = {
            "t": t,
            "vehicles_parked": self.current_status["vehicles_parked"] - 1,
        }
        self.status_dict_list.append(self.current_status)
