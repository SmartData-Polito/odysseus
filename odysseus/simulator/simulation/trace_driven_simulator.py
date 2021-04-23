import datetime

import pandas as pd

from odysseus.simulator.simulation.simulator import SharedMobilitySim
from odysseus.utils.time_utils import update_req_time_info
#from odysseus.utils.vehicle_utils import *
#from odysseus.supply_modelling.vehicle import Vehicle


class TraceDrivenSim (SharedMobilitySim):

    def init_data_structures(self):

        self.valid_zones = self.simInput.valid_zones

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
                and self.simInput.sim_scenario_conf["scooter_relocation"] \
                and self.simInput.sim_scenario_conf["scooter_relocation_strategy"] in ["proactive",
                                                                                       "reactive_post_charge",
                                                                                       "reactive_post_trip",
                                                                                       "predictive"]:
            self.scooterRelocationStrategy.generate_relocation_schedule(self.current_datetime, self.current_daytype,
                                                                        self.current_hour)
            self.update_relocation_schedule = False

        if self.update_relocation_schedule \
                and self.simInput.sim_scenario_conf["vehicle_relocation"] \
                and "vehicle_relocation_scheduling" in self.simInput.sim_scenario_conf.keys() \
                and self.simInput.sim_scenario_conf["vehicle_relocation_scheduling"]:
            self.vehicleRelocationStrategy.generate_relocation_schedule(self.current_datetime, self.current_daytype,
                                                                        self.current_hour)
            self.update_relocation_schedule = False
    
    def mobility_requests_generator(self):

        self.init_data_structures()
        sim_timestamps = []

        for booking_request in self.simInput.booking_requests_list:

            if booking_request["origin_id"] in self.valid_zones and booking_request["destination_id"] in self.valid_zones:

                sim_timestamps += [self.current_datetime]

                self.update_time_info()
                booking_request = update_req_time_info(booking_request)

                if self.simInput.supply_model_conf["scooter_relocation"] \
                        and self.simInput.supply_model_conf["scooter_relocation_strategy"] in ["predictive"]:
                    self.scooterRelocationStrategy.update_current_hour_stats(booking_request)

                yield self.env.timeout(booking_request["ia_timeout"])
                self.process_booking_request(booking_request)
