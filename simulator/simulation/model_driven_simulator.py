import datetime
import itertools

import pandas as pd
import numpy as np

from simulator.utils.vehicle_utils import get_soc_delta
from simulator.utils.vehicle_utils import soc_to_kwh
from simulator.simulation.simulator import EFFCS_Sim


class EventG_EFFCS_Sim (EFFCS_Sim):

	def init_data_structures (self):

		self.booking_request_arrival_rates = self.simInput.request_rates
		self.trip_kdes = self.simInput.trip_kdes
		self.od_distances = self.simInput.od_distances
		self.valid_zones = self.simInput.valid_zones
		self.update_data_structures()

	def update_time_info (self):

		self.hours_spent += 1

		self.current_datetime = self.start + datetime.timedelta(seconds=self.env.now)
		self.current_hour = self.current_datetime.hour
		self.current_weekday = self.current_datetime.weekday()
		if self.current_weekday in [5, 6]:
			self.current_daytype = "weekend"
		else:
			self.current_daytype = "weekday"

	def update_data_structures (self):

		self.current_arrival_rate = self.booking_request_arrival_rates[self.current_daytype][self.current_hour]
		self.current_trip_kde = self.trip_kdes[self.current_daytype][self.current_hour]

	def create_booking_request(self, timeout):

		self.update_time_info()
		self.update_data_structures()

		booking_request = {}

		booking_request["ia_timeout"] = timeout
		booking_request["start_time"] = self.current_datetime
		booking_request["date"] = self.current_datetime.date()
		booking_request["weekday"] = self.current_weekday
		booking_request["daytype"] = self.current_daytype
		booking_request["hour"] = self.current_hour
		trip_sample = self.current_trip_kde.sample()

		booking_request["origin_id"] = abs(trip_sample.astype(int)[0][0]) % len(self.valid_zones)
		booking_request["destination_id"] = abs(trip_sample.astype(int)[0][1]) % len(self.valid_zones)
		booking_request["euclidean_distance"] = self.od_distances.loc[
													booking_request["origin_id"],
													booking_request["destination_id"]
												] / 1000
		booking_request["driving_distance"] = booking_request["euclidean_distance"] * 1.4
		booking_request["duration"] = abs(booking_request["driving_distance"] / (15 + np.random.normal(5, 2.5))) * 3600
		booking_request["end_time"] = self.current_datetime + datetime.timedelta(minutes=booking_request["duration"])
		booking_request["soc_delta"] = -get_soc_delta(booking_request["driving_distance"])
		booking_request["soc_delta_kwh"] = soc_to_kwh(booking_request["soc_delta"])

		self.process_booking_request(booking_request)

	def mobility_requests_generator(self):

		for i in itertools.count():
			self.n_vehicles_per_zones_history += [{
				zone: len(self.available_vehicles_dict[zone]) for zone in self.available_vehicles_dict
			}]
			timeout_sec = (
				np.random.exponential(
					1 / self.simInput.sim_scenario_conf["requests_rate_factor"] / self.current_arrival_rate
				)
			)

			yield self.env.timeout(timeout_sec)
			self.create_booking_request(timeout_sec)

		self.n_vehicles_per_zones_history = pd.DataFrame(
			self.n_vehicles_per_zones_history,
			index=pd.DataFrame(self.sim_booking_requests)["start_time"]
		)
