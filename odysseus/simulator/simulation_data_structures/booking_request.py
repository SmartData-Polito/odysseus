from odysseus.simulator.simulation_data_structures.sim_event import SimEvent


class BookingRequest(SimEvent):

    def __init__(self, booking_request_dict):
        super().__init__("booking_request")
        self.booking_request_dict = booking_request_dict

    def search_max_soc_vehicle(self, available_vehicles_dict, vehicles_list, zone_id):
        available_vehicles_soc_dict = {
            k: vehicles_list[k].soc.level for k in available_vehicles_dict[zone_id]
        }
        max_soc = max(available_vehicles_soc_dict.values())
        max_soc_vehicle = max(available_vehicles_soc_dict, key=available_vehicles_soc_dict.get)
        if vehicles_list[max_soc_vehicle].soc.level > abs(
            vehicles_list[max_soc_vehicle].consumption_to_percentage(
                vehicles_list[max_soc_vehicle].distance_to_consumption(
                    self.booking_request_dict["driving_distance"] / 1000
                )
            )
        ):
            return True, max_soc_vehicle, max_soc
        else:
            return False, max_soc_vehicle, max_soc

    def search_vehicle(self, available_vehicles_dict, vehicles_list, neighbors_dict):
        available_vehicle_flag = False
        found_vehicle_flag = False
        available_vehicle_flag_same_zone = False
        available_vehicle_flag_not_same_zone = False
        max_soc_vehicle_id = -1
        max_soc_zone_id = -1

        if len(available_vehicles_dict[self.booking_request_dict["origin_id"]]):
            available_vehicle_flag = True
            available_vehicle_flag_same_zone = True
            found_vehicle_flag, max_soc_vehicle_origin, max_soc_origin = \
                self.search_max_soc_vehicle(
                    available_vehicles_dict, vehicles_list, self.booking_request_dict["origin_id"]
                )
            max_soc_vehicle_id = max_soc_vehicle_origin
            max_soc_zone_id = self.booking_request_dict["origin_id"]

        if not found_vehicle_flag:
            available_vehicle_flag = False
            found_vehicle_flag = False
            available_vehicle_flag_same_zone = False
            available_vehicle_flag_not_same_zone = False
            max_soc_vehicle_neighbor = None
            max_soc_neighbors = -1
            max_neighbor = None
            for neighbor in neighbors_dict[self.booking_request_dict["origin_id"]].dropna().values:
                if neighbor in available_vehicles_dict:
                    if len(available_vehicles_dict[neighbor]) and not found_vehicle_flag:
                        available_vehicle_flag = True
                        available_vehicle_flag_not_same_zone = True
                        found_vehicle_flag, max_soc_vehicle_neighbor, max_soc_neighbor = \
                            self.search_max_soc_vehicle(
                                available_vehicles_dict, vehicles_list, neighbor
                            )
                        if max_soc_neighbors < max_soc_neighbor:
                            max_neighbor = neighbor
                            max_soc_vehicle_neighbor = max_soc_vehicle_neighbor
            max_soc_vehicle_id = max_soc_vehicle_neighbor
            max_soc_zone_id = max_neighbor

        flags_return_dict = dict(
            available_vehicle_flag = available_vehicle_flag,
            found_vehicle_flag = found_vehicle_flag,
            available_vehicle_flag_same_zone = available_vehicle_flag_same_zone,
            available_vehicle_flag_not_same_zone = available_vehicle_flag_not_same_zone
        )

        return flags_return_dict, max_soc_vehicle_id, max_soc_zone_id
