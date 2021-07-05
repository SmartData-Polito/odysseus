import copy
import datetime
import pytz

import simpy

from odysseus.simulator.simulation_data_structures.zone import Zone
from odysseus.simulator.simulation_data_structures.vehicle import Vehicle
from odysseus.simulator.simulation_data_structures.charging_station import ChargingStation
from odysseus.simulator.simulation_data_structures.booking import Booking

from odysseus.simulator.simulation.charging_strategies import ChargingStrategy
from odysseus.simulator.simulation.scooter_relocation_strategies import ScooterRelocationStrategy
from odysseus.simulator.simulation.vehicle_relocation_strategies import VehicleRelocationStrategy

from odysseus.simulator.simulation_input.vehicle_conf import vehicle_conf
from odysseus.simulator.simulation_input.station_conf import station_conf
from odysseus.simulator.simulation.sim_metrics import SimMetrics

from odysseus.utils.bookings_utils import *


class SharedMobilitySim:

    def __init__(self, sim_input):

        self.start = datetime.datetime(
            sim_input.demand_model_config["year"],
            sim_input.demand_model_config["month_start"],
            1, tzinfo=pytz.UTC
        )

        if sim_input.demand_model_config["month_end"] == 13:
            self.end = datetime.datetime(
                sim_input.demand_model_config["year"] + 1,
                1,
                1, tzinfo=pytz.UTC
            )
        else:
            self.end = datetime.datetime(
                sim_input.demand_model_config["year"],
                sim_input.demand_model_config["month_end"],
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

        self.update_relocation_schedule = True

        self.sim_input = sim_input

        self.available_vehicles_dict = self.sim_input.supply_model.available_vehicles_dict
        self.neighbors_dict = self.sim_input.neighbors_dict
        self.closest_valid_zone = self.sim_input.closest_valid_zone
        self.vehicles_soc_dict = self.sim_input.supply_model.vehicles_soc_dict
        self.vehicles_zones = self.sim_input.supply_model.vehicles_zones

        if sim_input.supply_model_conf["distributed_cps"]:
            self.n_charging_poles_by_zone = self.sim_input.n_charging_poles_by_zone

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

        self.current_hour_origin_count = {}
        self.current_hour_destination_count = {}
        self.current_hour_n_bookings = 0

        self.tot_mobility_distance = 0
        self.tot_mobility_duration = 0

        self.list_n_vehicles_charging_system = []
        self.list_n_vehicles_charging_users = []
        self.list_n_vehicles_booked = []
        self.list_n_vehicles_available = []
        self.list_n_vehicles_dead = []
        self.list_n_scooters_relocating = []
        self.list_n_vehicles_relocating = []
        self.vehicles_zones_history = []
        self.charging_return_distance = []
        self.charging_outward_distance = []

        self.vehicles_list = []
        self.charging_stations_dict = {}
        self.zone_dict = {}

        for zone_id in self.sim_input.valid_zones:
            self.zone_dict[zone_id] = Zone(self.env, zone_id, self.start, self.available_vehicles_dict[zone_id])

        self.real_n_charging_zones = 0
        if self.sim_input.supply_model_conf["distributed_cps"]:
            for zone_id in self.sim_input.supply_model.n_charging_poles_by_zone:
                zone_n_cps = self.sim_input.supply_model.n_charging_poles_by_zone[zone_id]
                if zone_n_cps > 0:
                    self.charging_stations_dict[zone_id] = ChargingStation(
                        self.env, zone_n_cps, zone_id, station_conf, self.sim_input.supply_model_conf, self.start
                    )
                    self.real_n_charging_zones += zone_n_cps

        self.vehicles_list = []
        for i in range(self.sim_input.n_vehicles_sim):
            vehicle_object = Vehicle(
                self.env, i, self.vehicles_zones[i], self.vehicles_soc_dict[i],
                vehicle_conf, self.sim_input.supply_model.energy_mix, self.sim_input.supply_model_conf, self.start
            )
            self.vehicles_list.append(vehicle_object)

        if "alpha_policy" in self.sim_input.supply_model_conf:
            if self.sim_input.supply_model_conf["alpha_policy"] == "auto":
                self.sim_input.supply_model_conf["alpha"] = self.vehicles_list[0].consumption_to_percentage(
                    self.vehicles_list[0].distance_to_consumption(
                        self.sim_input.max_driving_distance / 1000
                    )
                )
            else:
                print("Policy for alpha not recognised!")
                exit(0)

        self.sim_metrics = SimMetrics()

        if self.sim_input.supply_model_conf["battery_swap"] \
                and self.sim_input.supply_model_conf["scooter_relocation"]:
            self.scooterRelocationStrategy = ScooterRelocationStrategy(self.env, self)
        elif self.sim_input.supply_model_conf["vehicle_relocation"]:
            self.vehicleRelocationStrategy = VehicleRelocationStrategy(self.env, self)

        self.chargingStrategy = ChargingStrategy(self.env, self)
        self.valid_zones = self.sim_input.valid_zones

        self.booking_request_arrival_rates = None
        self.trip_kdes = None
        self.current_arrival_rate = None
        self.current_trip_kde = None

    def update_time_info(self):

        self.hours_spent += 1

        self.current_datetime = self.start + datetime.timedelta(seconds=self.env.now)
        if self.current_hour != self.current_datetime.hour:
            self.current_hour = self.current_datetime.hour
            self.update_relocation_schedule = True
        self.current_weekday = self.current_datetime.weekday()
        if self.current_weekday in [5, 6]:
            self.current_daytype = "weekend"
        else:
            self.current_daytype = "weekday"

        if self.update_relocation_schedule \
                and self.sim_input.supply_model_conf["scooter_relocation"] \
                and self.sim_input.supply_model_conf["scooter_relocation_strategy"] in ["proactive",
                                                                                       "reactive_post_charge",
                                                                                       "reactive_post_trip",
                                                                                       "predictive"]:
            self.scooterRelocationStrategy.generate_relocation_schedule(self.current_datetime, self.current_daytype,
                                                                        self.current_hour)
            self.update_relocation_schedule = False

        if self.update_relocation_schedule \
                and self.sim_input.supply_model_conf["vehicle_relocation"] \
                and "vehicle_relocation_scheduling" in self.sim_input.supply_model_conf.keys() \
                and self.sim_input.supply_model_conf["vehicle_relocation_scheduling"]:
            self.vehicleRelocationStrategy.generate_relocation_schedule(
                self.current_datetime,
                self.current_daytype,
                self.current_hour
            )
            self.update_relocation_schedule = False

    def execute_booking (self, booking, vehicle_id, zone_id):

        booking_dict = booking.booking_dict

        self.tot_mobility_distance += booking_dict["driving_distance"]
        self.tot_mobility_duration += booking_dict["duration"]

        if self.sim_input.supply_model_conf["scooter_relocation"] \
                and self.sim_input.supply_model_conf["scooter_relocation_strategy"] in ["predictive"]:
            self.scooterRelocationStrategy.update_current_hour_stats(booking_dict)

        if "save_history" in self.sim_input.demand_model_config:
            if self.sim_input.demand_model_config["save_history"]:
                self.sim_bookings += [booking_dict]

        if vehicle_id in self.available_vehicles_dict[zone_id]:
            self.available_vehicles_dict[zone_id].remove(vehicle_id)
        if vehicle_id in self.vehicles_zones:
            del self.vehicles_zones[vehicle_id]

        self.n_booked_vehicles += 1
        yield self.env.process(booking.execute())
        booking_dict = booking.booking_dict
        self.n_booked_vehicles -= 1

        charging_relocation_zone_id = yield self.env.process(
            self.chargingStrategy.check_charge(booking_dict, self.vehicles_list[vehicle_id])
        )
        relocation_zone_id = charging_relocation_zone_id

        if self.sim_input.supply_model_conf["battery_swap"] \
                and self.sim_input.supply_model_conf["scooter_relocation"]:

            if self.sim_input.supply_model_conf["scooter_relocation_strategy"] == "reactive_post_trip":

                relocated, scooter_relocation = self.scooterRelocationStrategy.check_scooter_relocation(
                    booking_dict,
                    vehicles=[vehicle_id]
                )

                if relocated:
                    relocation_zone_id = scooter_relocation["end_zone_ids"][0]
                    yield self.env.process(
                        self.scooterRelocationStrategy.relocate_scooter_single_zone(scooter_relocation))

        if self.sim_input.supply_model_conf["vehicle_relocation"] \
                and "vehicle_relocation_scheduling" in self.sim_input.supply_model_conf:

            if self.sim_input.supply_model_conf["vehicle_relocation_scheduling"] \
                    and dict(self.sim_input.supply_model_conf["vehicle_scheduled_relocation_triggers"])["post_trip"]:

                relocated, vehicle_relocation = self.vehicleRelocationStrategy.check_vehicle_relocation(
                    booking_dict,
                    vehicles=[vehicle_id]
                )

                if relocated:
                    relocation_zone_id = vehicle_relocation["end_zone_id"]
                    yield self.env.process(self.vehicleRelocationStrategy.relocate_vehicle(vehicle_relocation))

        self.available_vehicles_dict[relocation_zone_id].append(vehicle_id)
        self.vehicles_zones[vehicle_id] = relocation_zone_id

    def process_booking_request(self, booking_request):

        booking_request_dict = booking_request.booking_request_dict

        self.list_n_vehicles_booked += [self.n_booked_vehicles]
        self.list_n_vehicles_charging_system += [self.chargingStrategy.n_vehicles_charging_system]
        self.list_n_vehicles_charging_users += [self.chargingStrategy.n_vehicles_charging_users]
        self.list_n_vehicles_dead += [self.chargingStrategy.n_dead_vehicles]

        n_vehicles_charging = self.chargingStrategy.n_vehicles_charging_system + self.chargingStrategy.n_vehicles_charging_users
        self.list_n_vehicles_available += [
            self.sim_input.n_vehicles_sim - n_vehicles_charging - self.n_booked_vehicles
        ]

        if self.sim_input.supply_model_conf["battery_swap"] \
                and self.sim_input.supply_model_conf["scooter_relocation"]:
            self.list_n_scooters_relocating += [self.scooterRelocationStrategy.n_scooters_relocating]
        elif self.sim_input.supply_model_conf["vehicle_relocation"]:
            self.list_n_vehicles_relocating += [self.vehicleRelocationStrategy.n_vehicles_relocating]

        self.charging_outward_distance = [self.chargingStrategy.charging_outward_distance]
        self.charging_return_distance = [self.chargingStrategy.charging_return_distance]

        if "save_history" in self.sim_input.demand_model_config:
            if self.sim_input.demand_model_config["save_history"]:
                self.sim_booking_requests += [booking_request_dict]
        self.n_booking_requests += 1

        flags_return_dict, chosen_vehicle_id, chosen_origin_id = booking_request.search_vehicle()

        available_vehicle_flag = flags_return_dict["available_vehicle_flag"]
        found_vehicle_flag = flags_return_dict["found_vehicle_flag"]
        available_vehicle_flag_same_zone = flags_return_dict["available_vehicle_flag_same_zone"]
        available_vehicle_flag_not_same_zone = flags_return_dict["available_vehicle_flag_not_same_zone"]

        if found_vehicle_flag:
            booking_request_dict = add_consumption_emission_info(
                booking_request_dict, self.vehicles_list[chosen_vehicle_id]
            )
            booking = Booking(
                self.env,
                booking_request_dict,
                self.zone_dict[chosen_origin_id],
                self.zone_dict[booking_request_dict["destination_id"]],
                self.vehicles_list[chosen_vehicle_id],
                self.sim_input.grid
            )
            self.env.process(self.execute_booking(booking, chosen_vehicle_id, chosen_origin_id))

        if available_vehicle_flag_same_zone:
            self.n_same_zone_trips += 1
        elif available_vehicle_flag_not_same_zone:
            self.n_not_same_zone_trips += 1

        if not found_vehicle_flag \
                and "scooter_relocation" in self.sim_input.supply_model_conf \
                and self.sim_input.supply_model_conf["scooter_relocation"] \
                and self.sim_input.supply_model_conf["scooter_relocation_strategy"] == "magic_relocation":

            relocated, scooter_relocation = self.scooterRelocationStrategy.check_scooter_relocation(booking_request_dict)

            if relocated:

                relocation_zone_id = scooter_relocation["end_zone_ids"][0]
                vehicle = scooter_relocation["vehicle_ids"][0]

                self.scooterRelocationStrategy.magically_relocate_scooter(scooter_relocation)
                self.available_vehicles_dict[scooter_relocation["start_zone_ids"][0]].remove(vehicle)
                self.available_vehicles_dict[relocation_zone_id].append(vehicle)
                self.vehicles_zones[vehicle] = relocation_zone_id

                available_vehicle_flag = True
                found_vehicle_flag = True

                self.env.process(
                    self.execute_booking(booking, vehicle, booking_request_dict["origin_id"])
                )
                self.n_same_zone_trips += 1

        if not found_vehicle_flag and self.sim_input.supply_model_conf["vehicle_relocation"] \
                and self.sim_input.supply_model_conf["vehicle_relocation_strategy"] == "magic_relocation":

            relocated, vehicle_relocation = \
                self.vehicleRelocationStrategy.check_vehicle_relocation(booking_request_dict)

            if relocated:
                available_vehicle_flag = True
                found_vehicle_flag = True

                self.env.process(
                    self.execute_booking(
                        booking,
                        vehicle_relocation["vehicle_ids"][0],
                        booking_request_dict["origin_id"]
                    )
                )
                self.n_same_zone_trips += 1

        if not available_vehicle_flag:
            self.n_no_close_vehicles += 1
            if "save_history" in self.sim_input.demand_model_config:
                if self.sim_input.demand_model_config["save_history"]:
                    self.sim_unsatisfied_requests += [booking_request_dict]
                    self.sim_no_close_vehicle_requests += [booking_request_dict]

        if not found_vehicle_flag and available_vehicle_flag:
            self.n_deaths += 1
            death = copy.deepcopy(booking_request_dict)
            death["hour"] = death["start_time"].hour
            death["plate"] = chosen_vehicle_id
            death["zone_id"] = chosen_origin_id
            if "save_history" in self.sim_input.demand_model_config:
                if self.sim_input.demand_model_config["save_history"]:
                    self.sim_booking_requests_deaths += [death]

    def mobility_requests_generator(self):
        pass

    def run(self):
        self.env.process(self.mobility_requests_generator())
        self.env.run(until=self.total_seconds)
