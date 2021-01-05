import copy
import datetime
import pytz
import json
from random import sample

import simpy

from e3f2s.simulator.simulation_data_structures.zone import Zone
from e3f2s.simulator.simulation_data_structures.vehicle import Vehicle
from e3f2s.simulator.simulation_data_structures.charging_station import ChargingStation

from e3f2s.simulator.simulation.charging_strategies import ChargingStrategy
from e3f2s.simulator.simulation.scooter_relocation_strategies import ScooterRelocationStrategy

from e3f2s.simulator.simulation_input.vehicle_conf import vehicle_conf
from e3f2s.simulator.simulation_input.energymix_conf import energymix_conf
from e3f2s.simulator.simulation_input.station_conf import station_conf
from e3f2s.utils.cost_utils import get_fuelcost_from_energy,maintenance_costs,bookings_revenues, ev_residual_value_revenue


class SharedMobilitySim:

    def __init__(self, simInput):

        self.start = datetime.datetime(
            simInput.sim_general_conf["year"],
            simInput.sim_general_conf["month_start"],
            1, tzinfo=pytz.UTC
        )

        if simInput.sim_general_conf["month_end"] == 13:
            self.end = datetime.datetime(
                simInput.sim_general_conf["year"] + 1,
                1,
                1, tzinfo=pytz.UTC
            )
        else:
            self.end = datetime.datetime(
                simInput.sim_general_conf["year"],
                simInput.sim_general_conf["month_end"],
                1, tzinfo=pytz.UTC
            )

        self.total_seconds = (self.end - self.start).total_seconds()
        self.hours_spent = 0
        self.current_datetime = self.start
        self.current_hour = self.current_datetime.hour
        self.current_weekday = self.current_datetime.weekday()
        if self.start.weekday() in [5, 6]:
            self.current_daytype = "weekend"
        else:
            self.current_daytype = "weekday"

        self.simInput = simInput

        self.available_vehicles_dict = self.simInput.available_vehicles_dict

        self.neighbors_dict = self.simInput.neighbors_dict

        if simInput.sim_scenario_conf["distributed_cps"]:
            self.n_charging_poles_by_zone = self.simInput.n_charging_poles_by_zone

        self.vehicles_soc_dict = self.simInput.vehicles_soc_dict
        self.vehicles_zones = self.simInput.vehicles_zones

        self.env = simpy.Environment()

        self.sim_booking_requests = []
        self.sim_bookings = []
        self.sim_booking_requests_deaths = []
        self.sim_unsatisfied_requests = []
        self.sim_no_close_vehicle_requests = []

        self.n_booking_requests = 0
        self.n_same_zone_trips = 0
        self.n_not_same_zone_trips = 0
        self.n_no_close_vehicles = 0
        self.n_deaths = 0
        self.n_booked_vehicles = 0

        self.list_n_vehicles_charging_system = []
        self.list_n_vehicles_charging_users = []
        self.list_n_vehicles_booked = []
        self.list_n_vehicles_available = []
        self.list_n_vehicles_dead = []
        self.charging_return_distance = []

        self.vehicles_list = []
        self.charging_stations_dict = {}
        self.zone_dict = {}

        for zone_id in self.simInput.valid_zones:
            self.zone_dict[zone_id] = Zone(self.env, zone_id, self.start, self.available_vehicles_dict[zone_id])

        if self.simInput.sim_scenario_conf["distributed_cps"]:
            for zone_id in self.simInput.n_charging_poles_by_zone:
                zone_n_cps = self.simInput.n_charging_poles_by_zone[zone_id]
                if zone_n_cps > 0:
                    self.charging_stations_dict[zone_id] = ChargingStation(
                        self.env, zone_n_cps, zone_id, station_conf, self.simInput.sim_scenario_conf, self.start
                    )

        self.vehicles_list = []
        for i in range(self.simInput.n_vehicles_sim):
            vehicle_object = Vehicle(
                self.env, i, self.vehicles_zones[i], self.vehicles_soc_dict[i],
                vehicle_conf, energymix_conf, self.simInput.sim_scenario_conf, self.start
            )
            self.vehicles_list.append(vehicle_object)

        if "alpha_policy" in self.simInput.sim_scenario_conf:
            if self.simInput.sim_scenario_conf["alpha_policy"] == "auto":
                self.simInput.sim_scenario_conf["alpha"] = self.vehicles_list[0].consumption_to_percentage(
                    self.vehicles_list[0].distance_to_consumption(
                        self.simInput.max_driving_distance / 1000
                    )
                )
            else:
                print("Policy for alpha not recognised!")
                exit(0)

        self.chargingStrategy = ChargingStrategy(self.env, self)
        self.scooterRelocationStrategy = ScooterRelocationStrategy(self.env, self)

    def schedule_booking (self, booking_request, vehicle, zone_id):

        if "save_history" in self.simInput.sim_general_conf:
            if self.simInput.sim_general_conf["save_history"]:
                self.sim_bookings += [booking_request]

        self.available_vehicles_dict[zone_id].remove(vehicle)
        del self.vehicles_zones[vehicle]
        booking_request["start_soc"] = self.vehicles_list[vehicle].soc.level
        #booking_request["start_soc"] = self.vehicles_soc_dict[vehicle_id]
        #del self.vehicles_soc_dict[vehicle_id]

        self.n_booked_vehicles += 1

        booking_request["plate"] = vehicle

        # yield self.env.timeout(booking_request["duration"])

        self.zone_dict[booking_request["origin_id"]].remove_vehicle(booking_request["start_time"])
        #print(self.vehicles_list[vehicle_id].soc.level)
        yield self.env.process(self.vehicles_list[vehicle].booking(booking_request))
        self.zone_dict[booking_request["destination_id"]].add_vehicle(
            booking_request["start_time"] + datetime.timedelta(seconds=booking_request['duration'])
        )
        #print(self.vehicles_list[vehicle_id].soc.level)

        #self.vehicles_soc_dict[vehicle_id] = booking_request["start_soc"] + booking_request["soc_delta"]
        #booking_request["end_soc"] = self.vehicles_soc_dict[vehicle_id]
        booking_request["end_soc"] = self.vehicles_list[vehicle].soc.level
        #self.vehicles_zones[vehicle_id] = booking_request["destination_id"]

        self.n_booked_vehicles -= 1

        relocation_zone_id = yield self.env.process(
            self.chargingStrategy.check_charge(booking_request, self.vehicles_list[vehicle])
        )

        self.available_vehicles_dict[relocation_zone_id].append(vehicle)
        self.vehicles_zones[vehicle] = relocation_zone_id

    def process_booking_request(self, booking_request):

        self.list_n_vehicles_booked += [self.n_booked_vehicles]
        self.list_n_vehicles_charging_system += [self.chargingStrategy.n_vehicles_charging_system]
        self.list_n_vehicles_charging_users += [self.chargingStrategy.n_vehicles_charging_users]
        self.list_n_vehicles_dead += [self.chargingStrategy.n_dead_vehicles]

        n_vehicles_charging = self.chargingStrategy.n_vehicles_charging_system + self.chargingStrategy.n_vehicles_charging_users
        self.list_n_vehicles_available += [
            self.simInput.n_vehicles_sim - n_vehicles_charging - self.n_booked_vehicles
        ]

        self.charging_return_distance = [self.chargingStrategy.charging_return_distance]

        if "save_history" in self.simInput.sim_general_conf:
            if self.simInput.sim_general_conf["save_history"]:
                self.sim_booking_requests += [booking_request]
        self.n_booking_requests += 1

        available_vehicle_flag = False
        found_vehicle_flag = False
        available_vehicle_flag_same_zone = False
        available_vehicle_flag_not_same_zone = False

        def find_vehicle (zone_id):
            #available_vehicles_soc_dict = {k: self.vehicles_soc_dict[k] for k in self.available_vehicles_dict[zone_id]}
            available_vehicles_soc_dict = {k: self.vehicles_list[k].soc.level for k in self.available_vehicles_dict[zone_id]}
            max_soc = max(available_vehicles_soc_dict.values())
            max_soc_vehicle = max(available_vehicles_soc_dict, key=available_vehicles_soc_dict.get)
            if self.vehicles_list[max_soc_vehicle].soc.level > abs(
                    self.vehicles_list[max_soc_vehicle].consumption_to_percentage(
                        self.vehicles_list[max_soc_vehicle].distance_to_consumption(booking_request["driving_distance"] / 1000)
                    )
            ):
                return True, max_soc_vehicle, max_soc
            else:
                return False, max_soc_vehicle, max_soc

        if len(self.available_vehicles_dict[booking_request["origin_id"]]):
            available_vehicle_flag = True
            available_vehicle_flag_same_zone = True
            found_vehicle_flag, max_soc_vehicle_origin, max_soc_origin = \
                find_vehicle(booking_request["origin_id"])

        if found_vehicle_flag:
            booking_request["soc_delta"] = self.vehicles_list[max_soc_vehicle_origin].consumption_to_percentage(
                        self.vehicles_list[max_soc_vehicle_origin].distance_to_consumption(
                            booking_request["driving_distance"] / 1000
                        )
                    )
            booking_request["avg_speed_kmh"] = (booking_request["driving_distance"] / 1000)/\
                                               (booking_request['duration'] / 3600)
            booking_request["welltotank_kwh"] = self.vehicles_list[max_soc_vehicle_origin].welltotank_energy_from_perc(
                booking_request["soc_delta"]
            )
            booking_request["tanktowheel_kwh"] = self.vehicles_list[max_soc_vehicle_origin].tanktowheel_energy_from_perc(
                booking_request["soc_delta"]
            )
            booking_request["soc_delta_kwh"] = booking_request["welltotank_kwh"] + booking_request["tanktowheel_kwh"]
            booking_request["welltotank_emissions"] = self.vehicles_list[
                max_soc_vehicle_origin].distance_to_welltotank_emission(booking_request["driving_distance"] / 1000)
            booking_request["tanktowheel_emissions"] = self.vehicles_list[
                max_soc_vehicle_origin].distance_to_tanktowheel_emission(booking_request["driving_distance"] / 1000)
            booking_request["co2_emissions"] = booking_request["welltotank_emissions"] + \
                                               booking_request["tanktowheel_emissions"]
            booking_request["energy_cost"] = get_fuelcost_from_energy(
                self.simInput.sim_scenario_conf["engine_type"], booking_request["tanktowheel_kwh"] * 3.6
            )
            booking_request["maintenance_cost"] = maintenance_costs(
                self.simInput.sim_scenario_conf["engine_type"], booking_request["driving_distance"] / 1000
            )
            booking_request["booking_revenue"] = bookings_revenues[self.simInput.sim_scenario_conf["engine_type"]][
                self.simInput.sim_scenario_conf["vehicle_model_name"]
            ]["cost_permin"] * (booking_request['duration'] / 60)
            if self.simInput.sim_scenario_conf["engine_type"] == "electric":
                booking_request["depreciation_vehicle"] = (
                        ev_residual_value_revenue["ICEV_depreciation_perkm"] +
                        ev_residual_value_revenue["battery_depreciation_perkm"]
                ) * booking_request["driving_distance"] / 1000
            elif self.simInput.sim_scenario_conf["engine_type"] in ["gasoline", "diesel","lpg","cng"]:
                booking_request["depreciation_vehicle"] = (
                        ev_residual_value_revenue["ICEV_depreciation_perkm"]
                ) * booking_request["driving_distance"] / 1000
            self.env.process(
                self.schedule_booking(booking_request, max_soc_vehicle_origin, booking_request["origin_id"])
            )
            self.n_same_zone_trips += 1
        else:
            available_vehicle_flag = False
            found_vehicle_flag = False
            available_vehicle_flag_same_zone = False
            available_vehicle_flag_not_same_zone = False
            max_soc_vehicle_neighbors = None
            max_soc_neighbors = -1
            max_neighbor = None
            for neighbor in self.neighbors_dict[booking_request["origin_id"]].dropna().values:
                if neighbor in self.available_vehicles_dict:
                    if len(self.available_vehicles_dict[neighbor]) and not found_vehicle_flag:
                        available_vehicle_flag = True
                        available_vehicle_flag_not_same_zone = True
                        found_vehicle_flag, max_soc_vehicle_neighbor, max_soc_neighbor = find_vehicle(neighbor)
                        if max_soc_neighbors < max_soc_neighbor:
                            max_neighbor = neighbor
                            max_soc_vehicle_neighbors = max_soc_vehicle_neighbor
            if found_vehicle_flag:
                self.env.process(
                    self.schedule_booking(booking_request, max_soc_vehicle_neighbors, max_neighbor)
                )
                self.n_not_same_zone_trips += 1

        if not found_vehicle_flag and self.simInput.sim_scenario_conf["scooter_relocation"] \
                and self.simInput.sim_scenario_conf["scooter_relocation_strategy"] == "magic_relocation":

            relocated, relocation_zone_id, relocated_vehicle = \
                self.scooterRelocationStrategy.check_scooter_relocation(booking_request)

            if relocated:

                available_vehicle_flag = True
                available_vehicle_flag_same_zone = True
                found_vehicle_flag = True

                self.env.process(
                    self.schedule_booking(booking_request, relocated_vehicle, booking_request["origin_id"])
                )
                self.n_same_zone_trips += 1

        if not available_vehicle_flag:
            self.n_no_close_vehicles += 1
            if "save_history" in self.simInput.sim_general_conf:
                if self.simInput.sim_general_conf["save_history"]:
                    self.sim_unsatisfied_requests += [booking_request]
                    self.sim_no_close_vehicle_requests += [booking_request]

        if not found_vehicle_flag and available_vehicle_flag:
            self.n_deaths += 1
            death = copy.deepcopy(booking_request)
            death["hour"] = death["start_time"].hour
            if available_vehicle_flag_same_zone and available_vehicle_flag_not_same_zone:
                if max_soc_origin > max_soc_neighbor:
                    death["plate"] = max_soc_vehicle_origin
                    death["zone_id"] = booking_request["origin_id"]
                else:
                    death["plate"] = max_soc_vehicle_neighbor
                    death["zone_id"] = max_neighbor
            elif available_vehicle_flag_same_zone:
                death["plate"] = max_soc_vehicle_origin
                death["zone_id"] = booking_request["origin_id"]
            elif available_vehicle_flag_not_same_zone:
                death["plate"] = max_soc_vehicle_neighbor
                death["zone_id"] = max_neighbor
            if "save_history" in self.simInput.sim_general_conf:
                if self.simInput.sim_general_conf["save_history"]:
                    self.sim_booking_requests_deaths += [death]

    def run (self):
        self.env.process(self.mobility_requests_generator())
        self.env.run(until=self.total_seconds)
