import copy
import itertools
import numpy as np
import simpy
# import datetime

from odysseus.simulator.simulation_data_structures.sim_booking import SimBooking

from odysseus.simulator.simulation.charging_strategies import ChargingStrategy
from odysseus.simulator.simulation.relocation_strategies import RelocationStrategy

from odysseus.supply_modelling.service_stations.station_conf import station_conf
from odysseus.simulator.simulation.sim_metrics import SimMetrics


from odysseus.simulator.simulation_data_structures.sim_booking_request import SimBookingRequest

from odysseus.utils.time_utils import *
from odysseus.utils.bookings_utils import *

from functools import partial, wraps


np.random.seed(44)

sim_events = list()


def trace(env, callback):

    def get_wrapper(env_step, callback):
        """Generate the wrapper for env.step()."""
        @wraps(env_step)
        def tracing_step():
            if len(env._queue):
                t, prio, eid, event = env._queue[0]
                callback(t, prio, eid, event)
            return env_step()
        return tracing_step

    env.step = get_wrapper(env.step, callback)


def monitor(data, t, prio, eid, event):
    data.append((datetime.datetime.now(), t, eid, type(event)))


monitor = partial(monitor, sim_events)


class SharedMobilitySim:

    def __init__(self, sim_input):

        self.start = sim_input.start
        self.end = sim_input.end
        self.total_seconds = sim_input.total_seconds
        self.total_days = sim_input.total_days
        self.current_datetime = self.start
        self.current_hour = self.current_datetime.hour
        self.current_weekday = self.current_datetime.weekday()
        self.update_relocation_schedule = True
        self.sim_input = sim_input

        if sim_input.demand_model_config["demand_model_type"] != "trace":
            for daytype in self.sim_input.demand_model.week_config["week_slots"]:
                if self.start.weekday() in self.sim_input.demand_model.week_config["week_slots"][daytype]:
                    self.current_daytype = daytype

        self.available_vehicles_dict = self.sim_input.supply_model.available_vehicles_dict
        self.neighbors_dict = self.sim_input.neighbors_dict
        self.closest_valid_zone = self.sim_input.closest_valid_zone
        self.vehicles_soc_dict = self.sim_input.supply_model.vehicles_soc_dict
        self.vehicles_zones = self.sim_input.supply_model.vehicles_zones

        if sim_input.supply_model_config["distributed_cps"]:
            self.n_charging_poles_by_zone = self.sim_input.n_charging_poles_by_zone

        self.env = simpy.Environment()
        # trace(self.env, monitor)

        self.sim_booking_requests = []
        self.sim_bookings = []
        self.sim_booking_requests_deaths = []
        self.sim_unsatisfied_requests = []
        self.sim_no_close_vehicle_requests = []

        self.n_booking_requests = 0
        self.n_bookings = 0
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

        vehicle_config = {
            "vehicle_model_name": self.sim_input.supply_model_config["vehicle_model_name"],
            "engine_type": self.sim_input.supply_model_config["engine_type"],
            "fuel_capacity": self.sim_input.supply_model_config["fuel_capacity"],
            "vehicle_efficiency": self.sim_input.supply_model_config["vehicle_efficiency"],
        }

        self.sim_input.supply_model.init_for_simulation(
            self.env, self.start, station_conf, vehicle_config,
        )

        self.zone_dict = self.sim_input.supply_model.zone_dict
        self.charging_stations_dict = self.sim_input.supply_model.charging_stations_dict

        self.real_n_charging_zones = self.sim_input.supply_model.real_n_charging_zones
        self.vehicles_list = self.sim_input.supply_model.vehicles_list

        self.sim_metrics = SimMetrics()

        if self.sim_input.supply_model_config["relocation"]:
            self.relocation_strategy = RelocationStrategy(self.env, self)

        self.charging_strategy = ChargingStrategy(self.env, self)
        self.valid_zones = self.sim_input.valid_zones

        self.booking_request_arrival_rates = None
        self.trip_kdes = None
        self.current_arrival_rate = None
        self.current_trip_kde = None

        self.sim_start_dt = None
        self.sim_end_dt = None
        self.sim_exec_time_sec = None

        self.sim_events = list()

    def update_time_info(self):

        self.current_datetime = self.start + datetime.timedelta(seconds=self.env.now)
        if self.current_hour != self.current_datetime.hour:
            self.current_hour = self.current_datetime.hour
            self.update_relocation_schedule = True
        self.current_weekday = self.current_datetime.weekday()

        if self.sim_input.demand_model_config["demand_model_type"] != "trace":
            self.current_daytype = get_daytype_from_week_config(
                self.sim_input.demand_model.week_config, self.current_weekday
            )
        else:
            self.current_daytype = get_daytype_from_weekday(self.current_weekday)

        if self.update_relocation_schedule \
                and self.sim_input.supply_model_config["relocation"] \
                and self.sim_input.supply_model_config["relocation_strategy"] in ["proactive",
                                                                                   "reactive_post_charge",
                                                                                   "reactive_post_trip",
                                                                                   "predictive"]:
            self.relocation_strategy.generate_relocation_schedule(self.current_datetime, self.current_daytype,
                                                                  self.current_hour)
            self.update_relocation_schedule = False

    def execute_booking(self, booking, vehicle_id, zone_id):

        booking_dict = booking.booking_dict

        self.tot_mobility_distance += booking_dict["driving_distance"]
        self.tot_mobility_duration += booking_dict["duration"]

        if self.sim_input.supply_model_config["relocation"] \
                and self.sim_input.supply_model_config["relocation_strategy"] in ["predictive", "proactive"]:
            self.relocation_strategy.update_current_hour_stats(booking_dict)

        if "save_history" in self.sim_input.sim_general_config:
            if self.sim_input.sim_general_config["save_history"]:
                self.sim_bookings += [booking_dict]

        self.update_time_info()

        if vehicle_id in self.available_vehicles_dict[zone_id]:
            self.available_vehicles_dict[zone_id].remove(vehicle_id)
        if vehicle_id in self.vehicles_zones:
            del self.vehicles_zones[vehicle_id]

        self.n_booked_vehicles += 1

        yield self.env.process(booking.execute_booking())

        booking_dict = booking.booking_dict
        self.n_booked_vehicles -= 1

        charging_relocation_zone_id = yield self.env.process(
            self.charging_strategy.check_charge(booking_dict, self.vehicles_list[vehicle_id])
        )
        relocation_zone_id = charging_relocation_zone_id

        self.available_vehicles_dict[relocation_zone_id].append(vehicle_id)
        self.vehicles_zones[vehicle_id] = relocation_zone_id

        self.update_time_info()

    def process_booking_request(self, booking_request):

        booking_request_dict = booking_request.booking_request_dict

        booking_request_dict["req_id"] = self.n_booking_requests
        self.n_booking_requests += 1

        if "save_history" in self.sim_input.sim_general_config:
            if self.sim_input.sim_general_config["save_history"]:
                self.sim_booking_requests += [booking_request_dict]
                self.list_n_vehicles_booked += [self.n_booked_vehicles]
                self.list_n_vehicles_charging_system += [self.charging_strategy.n_vehicles_charging_system]
                self.list_n_vehicles_charging_users += [self.charging_strategy.n_vehicles_charging_users]
                self.list_n_vehicles_dead += [self.charging_strategy.n_dead_vehicles]
                n_vehicles_charging = self.charging_strategy.n_vehicles_charging_system + self.charging_strategy.n_vehicles_charging_users
                self.list_n_vehicles_available += [
                    self.sim_input.n_vehicles_sim - n_vehicles_charging - self.n_booked_vehicles
                ]

        if self.sim_input.supply_model_config["relocation"]:
            self.list_n_scooters_relocating += [self.relocation_strategy.n_scooters_relocating]

        self.charging_outward_distance = [self.charging_strategy.charging_outward_distance]
        self.charging_return_distance = [self.charging_strategy.charging_return_distance]

        flags_return_dict, chosen_vehicle_id, chosen_origin_id = booking_request.search_vehicle(
            self.sim_input.demand_model_config["vehicle_research_policy"]
        )

        available_vehicle_flag = flags_return_dict["available_vehicle_flag"]
        found_vehicle_flag = flags_return_dict["found_vehicle_flag"]
        available_vehicle_flag_same_zone = flags_return_dict["available_vehicle_flag_same_zone"]
        available_vehicle_flag_not_same_zone = flags_return_dict["available_vehicle_flag_not_same_zone"]

        if found_vehicle_flag:
            self.n_bookings += 1
            booking_request_dict = add_consumption_emission_info(
                booking_request_dict, self.vehicles_list[chosen_vehicle_id]
            )
            booking = SimBooking(
                self.env,
                booking_request,
                self.zone_dict[chosen_origin_id],
                self.zone_dict[booking_request_dict["destination_id"]],
                self.vehicles_list[chosen_vehicle_id],
            )
            self.env.process(self.execute_booking(booking, chosen_vehicle_id, chosen_origin_id))

        if available_vehicle_flag_same_zone:
            self.n_same_zone_trips += 1
        elif available_vehicle_flag_not_same_zone:
            self.n_not_same_zone_trips += 1

        if not found_vehicle_flag \
                and "relocation" in self.sim_input.supply_model_config \
                and self.sim_input.supply_model_config["relocation"] \
                and self.sim_input.supply_model_config["relocation_strategy"] == "magic_relocation":

            relocated, scooter_relocation = self.relocation_strategy.check_scooter_relocation(booking_request_dict)

            if relocated:

                relocation_zone_id = scooter_relocation["end_zone_ids"][0]
                vehicle = scooter_relocation["vehicle_ids"][0]

                self.relocation_strategy.magically_relocate_scooter(scooter_relocation)
                self.available_vehicles_dict[scooter_relocation["start_zone_ids"][0]].remove(vehicle)
                self.available_vehicles_dict[relocation_zone_id].append(vehicle)
                self.vehicles_zones[vehicle] = relocation_zone_id

                available_vehicle_flag = True
                found_vehicle_flag = True

                self.env.process(
                    self.execute_booking(booking, vehicle, booking_request_dict["origin_id"])
                )
                self.n_same_zone_trips += 1

        if not available_vehicle_flag:
            self.n_no_close_vehicles += 1
            if "save_history" in self.sim_input.sim_general_config:
                if self.sim_input.sim_general_config["save_history"]:
                    self.sim_unsatisfied_requests += [booking_request_dict]
                    self.sim_no_close_vehicle_requests += [booking_request_dict]

        if not found_vehicle_flag and available_vehicle_flag:
            self.n_deaths += 1
            death = copy.deepcopy(booking_request_dict)
            death["hour"] = death["start_time"].hour
            death["plate"] = chosen_vehicle_id
            death["zone_id"] = chosen_origin_id
            if "save_history" in self.sim_input.sim_general_config:
                if self.sim_input.sim_general_config["save_history"]:
                    self.sim_booking_requests_deaths += [death]

    def mobility_requests_generator_from_model(self):

        hours_spent = 0
        self.update_time_info()
        last_current_hour = self.current_hour

        for i in itertools.count():

            for booking_request_dict in self.sim_input.demand_model.generate_booking_requests_sim(
                    self.current_datetime,
                    self.sim_input.demand_model_config["requests_rate_factor"],
                    self.sim_input.demand_model_config["avg_speed_kmh_mean"],
                    self.sim_input.demand_model_config["max_duration"],
                    self.sim_input.demand_model_config["fixed_driving_distance"]
            ):

                yield self.env.timeout(booking_request_dict["ia_timeout"])
                self.update_time_info()

                booking_request = SimBookingRequest(
                    self.env, self.sim_input, self.vehicles_list, booking_request_dict
                )

                self.process_booking_request(booking_request)

            if self.sim_input.demand_model_config["demand_model_type"] == "od_matrices":
                yield self.env.timeout(3600 - self.current_datetime.minute * 60)
                self.update_time_info()

            if self.current_hour != last_current_hour:
                last_current_hour = self.current_hour
                hours_spent += 1

            if hours_spent >= self.sim_input.sim_general_config["max_sim_hours"]:
                break

    def mobility_requests_generator_from_trace(self):

        hours_spent = 0
        self.update_time_info()
        last_current_hour = self.current_hour

        print(datetime.datetime.now(), "Simulation started ...")

        for booking_request_dict in self.sim_input.booking_requests_list:

            if booking_request_dict["origin_id"] in self.valid_zones\
                    and booking_request_dict["destination_id"] in self.valid_zones:

                # booking_request_dict = update_req_time_info(booking_request_dict)
                #
                # if self.sim_input.supply_model_config["relocation"] \
                #         and self.sim_input.supply_model_config["relocation_strategy"] in ["predictive"]:
                #     self.relocation_strategy.update_current_hour_stats(booking_request_dict)

                yield self.env.timeout(booking_request_dict["ia_timeout"])

                self.update_time_info()

                booking_request = SimBookingRequest(
                    self.env, self.sim_input, self.vehicles_list, booking_request_dict
                )
                self.process_booking_request(booking_request)

                if self.current_hour != last_current_hour:
                    last_current_hour = self.current_hour
                    hours_spent += 1

                if hours_spent >= self.sim_input.sim_general_config["max_sim_hours"]:
                    break

    def mobility_requests_generator(self):
        if self.sim_input.demand_model_config["demand_model_type"] in ["od_matrices", "poisson_kde"]:
            self.env.process(self.mobility_requests_generator_from_model())
        elif self.sim_input.demand_model_config["demand_model_type"] == "trace":
            self.env.process(self.mobility_requests_generator_from_trace())

    def run(self):
        self.sim_start_dt = datetime.datetime.now()
        # trace(self.env, monitor)
        self.mobility_requests_generator()
        self.env.run(until=self.total_seconds)
        self.sim_events = sim_events
        self.sim_end_dt = datetime.datetime.now()
        self.sim_exec_time_sec = (
            self.sim_end_dt - self.sim_start_dt
        ).total_seconds()
