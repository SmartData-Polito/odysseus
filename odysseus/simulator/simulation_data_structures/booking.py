from odysseus.simulator.simulation_data_structures.sim_event import SimEvent


class Booking(SimEvent):

    def __init__(self, booking_request_dict, vehicle_id):
        super().__init__("booking")
        self.booking_request_dict = booking_request_dict
