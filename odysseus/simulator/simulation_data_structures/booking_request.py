from odysseus.simulator.simulation_data_structures.sim_event import SimEvent


class BookingRequest(SimEvent):

    def __init__(self, booking_request_dict):
        super().__init__("booking_request")
        self.booking_request_dict = booking_request_dict

    def search_max_soc_vehicle(self, available_vehicles_dict, vehicles_list, booking_request_dict, zone_id):
        available_vehicles_soc_dict = {
            k: vehicles_list[k].soc.level for k in available_vehicles_dict[zone_id]
        }
        max_soc = max(available_vehicles_soc_dict.values())
        max_soc_vehicle = max(available_vehicles_soc_dict, key=available_vehicles_soc_dict.get)
        if vehicles_list[max_soc_vehicle].soc.level > abs(
            vehicles_list[max_soc_vehicle].consumption_to_percentage(
                vehicles_list[max_soc_vehicle].distance_to_consumption(
                    booking_request_dict["driving_distance"] / 1000
                )
            )
        ):
            return True, max_soc_vehicle, max_soc
        else:
            return False, max_soc_vehicle, max_soc
