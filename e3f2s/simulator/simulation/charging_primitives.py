import simpy
import datetime

import numpy as np

from e3f2s.simulator.simulation_input.sim_current_config.vehicle_config import vehicle_conf
from e3f2s.utils.vehicle_utils import *


def get_charging_time(soc_delta,
                      battery_capacity=vehicle_conf["battery_capacity"],
                      charging_efficiency=0.92,
                      charger_rated_power=3.7):
    return (soc_delta * 3600 * battery_capacity) / (charging_efficiency * charger_rated_power * 100)


def get_charging_soc(duration,
                     battery_capacity=vehicle_conf["battery_capacity"],
                     charging_efficiency=0.92,
                     charger_rated_power=3.7):
    return (charging_efficiency * charger_rated_power * 100 * duration) / (3600 * battery_capacity)


def init_charge(booking_request, vehicles_soc_dict, vehicle, beta):
    charge = {}
    charge["plate"] = vehicle
    charge["start_time"] = booking_request["end_time"]
    charge["date"] = charge["start_time"].date()
    charge["hour"] = charge["start_time"].hour
    charge["day_hour"] = \
        charge["start_time"].replace(minute=0, second=0, microsecond=0)
    charge["start_soc"] = vehicles_soc_dict[vehicle]
    charge["end_soc"] = beta
    charge["soc_delta"] = charge["end_soc"] - charge["start_soc"]
    charge["soc_delta_kwh"] = soc_to_kwh(charge["soc_delta"])
    return charge


class ChargingPrimitives:

    def __init__(self, env, sim):

        self.env = env

        self.simInput = sim.simInput

        self.vehicles_soc_dict = sim.vehicles_soc_dict

        self.vehicles_list = sim.vehicles_list

        self.charging_stations_dict = sim.charging_stations_dict

        self.zone_dict = sim.zone_dict

        self.workers = simpy.Resource(
            self.env,
            capacity=self.simInput.sim_scenario_conf["n_workers"]
        )

        if self.simInput.sim_scenario_conf["hub"]:
            self.charging_hub = simpy.Resource(
                self.env,
                capacity=self.simInput.hub_n_charging_poles
            )

        if self.simInput.sim_scenario_conf["distributed_cps"]:
            self.n_charging_poles_by_zone = self.simInput.n_charging_poles_by_zone
            self.charging_poles_dict = {}
            for zone, n in self.n_charging_poles_by_zone.items():
                if n > 0:
                    self.charging_poles_dict[zone] = simpy.Resource(
                        self.env,
                        capacity=n
                    )

        self.sim_charges = []
        self.sim_unfeasible_charge_bookings = []

        self.n_vehicles_charging_system = 0
        self.n_vehicles_charging_users = 0
        self.dead_vehicles = set()
        self.n_dead_vehicles = 0

        self.list_system_charging_bookings = []
        self.list_users_charging_bookings = []

    def charge_vehicle(
            self,
            charge_dict
    ):

        charge = charge_dict["charge"]
        resource = charge_dict["resource"]
        vehicle_id = charge_dict["vehicle"]
        operator = charge_dict["operator"]
        zone_id = charge_dict["zone_id"]
        timeout_outward = charge_dict["timeout_outward"]
        timeout_return = charge_dict["timeout_return"]
        cr_soc_delta = charge_dict["cr_soc_delta"]

        def check_queuing():
            if self.simInput.sim_scenario_conf["queuing"]:
                return True
            else:
                if resource.count < resource.capacity:
                    return True
                else:
                    return False

        charge["operator"] = operator
        charge["zone_id"] = zone_id
        charge["timeout_outward"] = timeout_outward
        charge["timeout_return"] = timeout_return
        charge["cr_soc_delta"] = cr_soc_delta
        charge["cr_soc_delta_kwh"] = soc_to_kwh(cr_soc_delta)

        if self.simInput.sim_scenario_conf["battery_swap"]:
            if operator == "system":
                if check_queuing():
                    with self.workers.request() as worker_request:
                        yield worker_request
                        self.n_vehicles_charging_system += 1
                        yield self.env.timeout(charge["timeout_outward"])
                        yield self.env.timeout(charge["duration"])
                        self.n_vehicles_charging_system -= 1
                        yield self.env.timeout(charge["timeout_return"])
                        self.vehicles_soc_dict[vehicle_id] = charge["end_soc"]
            elif operator == "users":
                self.n_vehicles_charging_users += 1
                yield self.env.timeout(charge["duration"])
                self.vehicles_soc_dict[vehicle_id] = charge["end_soc"]
                self.n_vehicles_charging_users -= 1

        else:
            if operator == "system":
                if check_queuing():
                    with self.workers.request() as worker_request:

                        yield worker_request

                        yield self.env.timeout(charge["timeout_outward"])
                        charge["start_soc"] -= charge["cr_soc_delta"]

                        yield self.env.timeout(charge["timeout_return"])
                        self.vehicles_soc_dict[vehicle_id] = charge["end_soc"]
                        charge["end_soc"] -= charge["cr_soc_delta"]

                    self.n_vehicles_charging_system += 1
                    self.zone_dict[charge["zone_id"]].add_vehicle(
                        charge["start_time"] + datetime.timedelta(seconds=charge["duration"])
                    )
                    yield self.env.process(
                        self.charging_stations_dict[zone_id].charge(
                            self.vehicles_list[vehicle_id], charge["start_time"], charge["cr_soc_delta"],
                            charge["duration"]
                        )
                    )
                    self.n_vehicles_charging_system -= 1

            elif operator == "users":
                if resource.count < resource.capacity:
                    with resource.request() as charging_request:
                        yield charging_request
                        self.n_vehicles_charging_users += 1
                        yield self.env.timeout(charge["duration"])
                    self.vehicles_soc_dict[vehicle_id] = charge["end_soc"]
                    self.n_vehicles_charging_users -= 1

        charge["end_time"] = charge["start_time"] + datetime.timedelta(seconds=charge["duration"])
        self.sim_charges += [charge]

    def check_system_charge(self, booking_request, vehicle):

        if self.vehicles_soc_dict[vehicle] < self.simInput.sim_scenario_conf["alpha"]:
            charge = init_charge(
                booking_request,
                self.vehicles_soc_dict,
                vehicle,
                self.simInput.sim_scenario_conf["beta"]
            )
            self.zone_dict[booking_request["destination_id"]].remove_vehicle(booking_request["end_time"])
            return True, charge
        else:
            return False, None

    def check_user_charge(self, booking_request, vehicle):

        if booking_request["end_soc"] < self.simInput.sim_scenario_conf["beta"]:
            if booking_request["end_soc"] < self.simInput.sim_scenario_conf["alpha"]:
                if np.random.binomial(1, self.simInput.sim_scenario_conf["willingness"]):
                    charge = init_charge(
                        booking_request,
                        self.vehicles_soc_dict,
                        vehicle,
                        self.simInput.sim_scenario_conf["beta"]
                    )
                    return True, charge
                else:
                    return False, None
            else:
                return False, None
        else:
            return False, None

    def get_timeout(self, origin_id, destination_id):
        distance = self.simInput.od_distances.loc[origin_id, destination_id] / 1000
        return distance / 15 * 3600

    def get_cr_soc_delta(self, origin_id, destination_id):
        distance = self.simInput.od_distances.loc[origin_id, destination_id] / 1000
        return get_soc_delta(distance)
