class Zone(object):
    def __init__(self, env, id, sim_start_time):
        self.env = env
        self.id = id
        self.vehicles = []
        self.current_status = {
            "time": sim_start_time,
            "vehicles_parked": 0,
        }
        self.status_dict_list = [
            self.current_status
        ]

    def add_vehicle(self, time):
        self.current_status = {
            "time": time,
            "vehicles_parked": self.current_status["vehicles_parked"] +1,
        }
        self.status_dict_list.append(self.current_status)

    def remove_vehicle(self, time):
        self.current_status = {
            "time": time,
            "vehicles_parked": self.current_status["vehicles_parked"] -1,
        }
        self.status_dict_list.append(self.current_status)


