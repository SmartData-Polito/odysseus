class Worker(object):

    def __init__(self, env, id, start_zone):
        self.env = env
        self.id = id
        self.current_position = start_zone
        self.busy = False
        self.n_jobs = 0

    def start_working(self):
        self.busy = True
        self.n_jobs += 1

    def stop_working(self):
        self.busy = False

    def update_position(self, zone_id):
        self.current_position = zone_id
