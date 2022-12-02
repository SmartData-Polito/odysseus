from odysseus.simulator.simulation_data_structures.sim_event import SimEvent
from odysseus.utils.bookings_utils import *


class SimBookingRequest(SimEvent):

    def __init__(
            self, env, sim_input, vehicles_list, booking_request_dict,
    ):
        super().__init__(env, "booking_request")
        self.sim_input = sim_input
        self.available_vehicles_dict = self.sim_input.supply_model.available_vehicles_dict
        self.neighbors_dict = self.sim_input.neighbors_dict
        self.closest_zones = self.sim_input.closest_zones
        self.vehicles_list = vehicles_list
        self.booking_request_dict = booking_request_dict

    def search_max_soc_vehicle(self, zone_id):
        available_vehicles_soc_dict = {
            k: self.vehicles_list[k].soc.level for k in self.available_vehicles_dict[zone_id]
        }
        max_soc = max(available_vehicles_soc_dict.values())
        max_soc_vehicle = max(available_vehicles_soc_dict, key=available_vehicles_soc_dict.get)
        trip_consumption_percentage = self.vehicles_list[max_soc_vehicle].consumption_to_percentage(
                self.vehicles_list[max_soc_vehicle].distance_to_consumption(
                    self.booking_request_dict["driving_distance"] / 1000
                )
            )
        if self.vehicles_list[max_soc_vehicle].soc.level > abs(
                trip_consumption_percentage
        ):
            return True, max_soc_vehicle, max_soc
        else:
            return False, max_soc_vehicle, max_soc

    def search_vehicle_in_zone(self, zone_id):

        available_vehicle_flag = False
        found_vehicle_flag = False
        available_vehicle_flag_same_zone = False

        max_soc_vehicle_id = -1
        max_soc_zone_id = -1

        if len(self.available_vehicles_dict[zone_id]):
            available_vehicle_flag = True
            found_vehicle_flag, max_soc_vehicle_origin, max_soc_origin = self.search_max_soc_vehicle(zone_id)
            max_soc_vehicle_id = max_soc_vehicle_origin
            max_soc_zone_id = self.booking_request_dict["origin_id"]
            if found_vehicle_flag:
                available_vehicle_flag_same_zone = True

        flags_return_dict = dict(
            available_vehicle_flag=available_vehicle_flag,
            found_vehicle_flag=found_vehicle_flag,
            available_vehicle_flag_same_zone=available_vehicle_flag_same_zone,
            available_vehicle_flag_not_same_zone=False
        )
        return flags_return_dict, max_soc_vehicle_id, max_soc_zone_id

    def search_vehicle_in_neighbors(self):

        available_vehicle_flag = False
        found_vehicle_flag = False
        available_vehicle_flag_same_zone = False
        available_vehicle_flag_not_same_zone = False

        max_soc_vehicle_neighbor = None
        max_soc_neighbors = -1
        max_neighbor = None

        for neighbor in self.neighbors_dict[self.booking_request_dict["origin_id"]].dropna().values:
            if neighbor in self.available_vehicles_dict:
                if len(self.available_vehicles_dict[neighbor]) and not found_vehicle_flag:
                    available_vehicle_flag = True
                    available_vehicle_flag_not_same_zone = True
                    found_vehicle_flag, max_soc_vehicle_neighbor, max_soc_neighbor = self.search_max_soc_vehicle(
                        neighbor
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

    def search_closest_vehicle(self):

        flags_return_dict = dict(
            available_vehicle_flag = False,
            found_vehicle_flag = False,
            available_vehicle_flag_same_zone = False,
            available_vehicle_flag_not_same_zone = False
        )
        chosen_vehicle_id = -1
        chosen_origin_id = -1

        for zone_id in self.closest_zones[self.booking_request_dict["origin_id"]]:

            flags_return_dict, chosen_vehicle_id, chosen_origin_id = self.search_max_soc_vehicle(zone_id)

            if flags_return_dict["found_vehicle_flag"]:
                if zone_id == self.booking_request_dict["origin_id"]:
                    flags_return_dict["available_vehicle_flag_same_zone"] = True
                else:
                    flags_return_dict["available_vehicle_flag_not_same_zone"] = True
                break

        return flags_return_dict, chosen_vehicle_id, chosen_origin_id

    def search_vehicle(self, vehicle_research_policy):

        if vehicle_research_policy == "zone":
            return self.search_vehicle_in_zone(
                int(self.booking_request_dict["origin_id"])
            )

        elif vehicle_research_policy == "neighbors_1":
            flags_return_dict, chosen_vehicle_id, chosen_origin_id = self.search_vehicle_in_zone(
                int(self.booking_request_dict["origin_id"])
            )
            if flags_return_dict["found_vehicle_flag"]:
                return flags_return_dict, chosen_vehicle_id, chosen_origin_id
            else:
                return self.search_vehicle_in_neighbors()

        elif vehicle_research_policy == "closest_vehicle":
            flags_return_dict, chosen_vehicle_id, chosen_origin_id = self.search_vehicle_in_zone(
                int(self.booking_request_dict["origin_id"])
            )
            if flags_return_dict["found_vehicle_flag"]:
                return flags_return_dict, chosen_vehicle_id, chosen_origin_id
            else:
                return self.search_closest_vehicle()
