from e3f2s.simulator.simulation.scooter_relocation_primitives import *


class ScooterRelocationStrategy(ScooterRelocationPrimitives):

    def check_scooter_relocation(self, booking_request):

        relocated = False
        relocation_zone_id = None
        relocated_vehicle = None

        if self.simInput.sim_scenario_conf["battery_swap"]:

            if self.simInput.sim_scenario_conf["scooter_relocation_strategy"] == "magic_relocation":

                available_vehicles_soc_dict = {}

                for zone_id in list(self.zone_dict):
                    if len(self.available_vehicles_dict[zone_id]):
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
