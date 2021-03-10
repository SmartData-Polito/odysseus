class Worker(object):

    def __init__(self, env, start_zone):
        self.env = env
        self.current_position = start_zone
        self.busy = False

    def start_working(self):
        self.busy = True

    def stop_working(self):
        self.busy = False

    def update_position(self, zone_id):
        self.current_position = zone_id
