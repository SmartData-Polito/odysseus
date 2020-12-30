import numpy as np
from e3f2s.simulator.simulation.scooter_relocation_primitives import *


class ScooterRelocationStrategy(ScooterRelocationPrimitives):

    def check_scooter_relocation(self, booking_request):

        relocated = False
        relocation_zone_id = None
        relocated_vehicle = None

        if self.simInput.supply_model_conf["battery_swap"]:

            if self.simInput.supply_model_conf["scooter_relocation_strategy"] == "magic_relocation":

                booking_request_zone_column = int(np.floor(
                    booking_request["origin_id"] / self.simInput.grid_matrix.shape[0]
                ))
                booking_request_zone_row = int(
                    booking_request["origin_id"] - booking_request_zone_column * self.simInput.grid_matrix.shape[0]
                )

                found_vehicle_flag = False
                r = 2  # excludes origin zone and its neighbors

                while not found_vehicle_flag and r < max(self.simInput.grid_matrix.shape):

                    zones_ring = []
                    available_vehicles_soc_dict = {}

                    i = booking_request_zone_row - r
                    j = booking_request_zone_column - r
                    if i >= 0 and j >= 0:
                        while j < booking_request_zone_column + r and j < self.simInput.grid_matrix.shape[1]:
                            zones_ring.append(self.simInput.grid_matrix.iloc[i, j])
                            j += 1

                    i = booking_request_zone_row - r
                    j = booking_request_zone_column + r
                    if i >= 0 and j < self.simInput.grid_matrix.shape[1]:
                        while i < booking_request_zone_row + r and i < self.simInput.grid_matrix.shape[0]:
                            zones_ring.append(self.simInput.grid_matrix.iloc[i, j])
                            i += 1

                    i = booking_request_zone_row + r
                    j = booking_request_zone_column + r
                    if i < self.simInput.grid_matrix.shape[0] and j < self.simInput.grid_matrix.shape[1]:
                        while j > booking_request_zone_column - r and j > 0:
                            zones_ring.append(self.simInput.grid_matrix.iloc[i, j])
                            j -= 1

                    i = booking_request_zone_row + r
                    j = booking_request_zone_column - r
                    if i < self.simInput.grid_matrix.shape[0] and j >= 0:
                        while i > booking_request_zone_row - r and i > 0:
                            zones_ring.append(self.simInput.grid_matrix.iloc[i, j])
                            i -= 1

                    for zone_id in zones_ring:
                        if zone_id in self.available_vehicles_dict and len(self.available_vehicles_dict[zone_id]):
                            for available_vehicle in self.available_vehicles_dict[zone_id]:
                                available_vehicles_soc_dict[available_vehicle] = self.vehicles_list[available_vehicle].soc.level

                    if len(available_vehicles_soc_dict):
                        max_soc_vehicle = max(available_vehicles_soc_dict, key=available_vehicles_soc_dict.get)
                        max_soc_vehicle_zone = self.vehicles_zones[max_soc_vehicle]

                        if self.vehicles_list[max_soc_vehicle].soc.level > abs(
                            self.vehicles_list[max_soc_vehicle].consumption_to_percentage(
                                self.vehicles_list[max_soc_vehicle].distance_to_consumption(
                                    booking_request["driving_distance"] / 1000
                                )
                            )
                        ):
                            found_vehicle_flag = True

                    r += 1

                if found_vehicle_flag:

                    relocated = True
                    relocation_zone_id = booking_request["origin_id"]
                    relocated_vehicle = max_soc_vehicle

                    scooter_relocation = init_scooter_relocation(
                        relocated_vehicle,
                        booking_request["start_time"],
                        max_soc_vehicle_zone,
                        relocation_zone_id
                    )

                    self.relocate_scooter(scooter_relocation)

        return relocated, relocation_zone_id, relocated_vehicle
