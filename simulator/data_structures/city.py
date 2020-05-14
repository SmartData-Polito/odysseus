import os
import datetime
import pytz

import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.neighbors import KernelDensity

from city_data_manager.city_data_source.utils.geospatial_utils import get_city_grid

from simulator.utils.bookings_utils import pre_process_time
from simulator.loading.Loader import Loader
from simulator.utils.vehicle_utils import get_soc_delta


class City:

	def __init__(self, city_name, data_source_id, sim_general_conf, kde_bw=1):

		self.city_name = city_name
		self.data_source_id = data_source_id
		self.sim_general_conf = sim_general_conf
		self.kde_bw = kde_bw

		year = self.sim_general_conf["year"]
		start_month = self.sim_general_conf["month_start"]
		end_month = self.sim_general_conf["month_end"]
		self.bin_side_length = self.sim_general_conf["bin_side_length"]

		self.bookings = pd.DataFrame()
		self.trips_origins = pd.DataFrame()
		self.trips_destinations = pd.DataFrame()
		for month in range(start_month, end_month):
			loader = Loader(self.city_name, data_source_id, year, month, self.bin_side_length)
			bookings = loader.read_trips()
			origins, destinations = loader.read_origins_destinations()
			self.bookings = pd.concat([self.bookings, bookings], ignore_index=True)
			self.trips_origins = pd.concat([
				self.trips_origins, origins.drop(["index_right", "zone_id"], axis=1)
			], ignore_index=True)
			self.trips_destinations = pd.concat([
				self.trips_destinations, destinations.drop(["index_right", "zone_id"], axis=1)
			], ignore_index=True)

		self.grid = self.get_squared_grid()
		self.grid["zone_id"] = self.grid.index.values
		self.bookings = self.get_input_bookings_filtered()
		self.map_zones_on_trips(self.grid)

		self.valid_zones = self.get_valid_zones()
		self.grid = self.grid.loc[self.valid_zones]
		self.bookings = self.bookings.loc[
			(self.bookings.origin_id.isin(self.grid.index)) & (
				self.bookings.destination_id.isin(self.grid.index)
			)
		]
		self.grid["new_zone_id"] = range(len(self.grid))
		self.grid["initial_zone_id"] = self.grid.zone_id
		self.bookings[["origin_id", "destination_id"]] = self.bookings[[
			"origin_id", "destination_id"
		]].astype(int).replace(self.grid.new_zone_id.to_dict())
		self.grid["zone_id"] = self.grid.new_zone_id
		self.grid = self.grid.reset_index()
		self.original_valid_zones = self.valid_zones.copy()
		self.valid_zones = self.grid.index

		self.od_distances = self.get_od_distances()
		self.neighbors, self.neighbors_dict = self.get_neighbors_dicts()

		self.bookings.loc[:, "city"] = self.city_name
		self.request_rates = self.get_requests_rates()
		self.trip_kdes = self.get_trip_kdes()

	def get_squared_grid (self):

		locations = pd.concat([
				self.trips_origins.geometry, self.trips_destinations.geometry
		], ignore_index=True)
		locations.crs = "epsg:4326"
		squared_grid = get_city_grid(
			locations,
			self.bin_side_length
		)
		return squared_grid

	def map_zones_on_trips(self, zones):
		self.trips_origins = gpd.sjoin(
			self.trips_origins,
			zones,
			how='left',
			op='within'
		)
		self.trips_destinations = gpd.sjoin(
			self.trips_destinations,
			zones,
			how='left',
			op='within'
		)
		self.bookings["origin_id"] = self.trips_origins.zone_id
		self.bookings["destination_id"] = self.trips_destinations.zone_id

	def get_valid_zones(self):

		self.valid_zones = self.bookings.origin_id.value_counts().sort_values().tail(
			int(self.sim_general_conf["k_zones_factor"] * len(self.grid))
		).index
		origin_zones_count = self.bookings.origin_id.value_counts()
		dest_zones_count = self.bookings.destination_id.value_counts()
		valid_origin_zones = origin_zones_count[(origin_zones_count > 0)]
		valid_dest_zones = dest_zones_count[(dest_zones_count > 0)]
		self.valid_zones = self.valid_zones.intersection(
			valid_origin_zones.index.intersection(
				valid_dest_zones.index
			).astype(int)
		)
		return self.valid_zones

	def get_od_distances(self):

		points = self.grid.centroid.geometry
		od_distances = points.apply(lambda p: points.distance(p)) * 111.32 / 0.001
		od_distances = pd.DataFrame(
			od_distances,
			index=self.grid.zone_id.values,
			columns=self.grid.zone_id.values
		)
		#print(od_distances[od_distances > 0].min())
		return od_distances

	def get_neighbors_dicts(self):

		self.max_dist = self.od_distances.max().max()

		self.neighbors = self.od_distances[self.od_distances < 2 * self.bin_side_length - 1].apply(
			lambda x: pd.Series(x.sort_values().dropna().iloc[1:].index.values),
			axis=1
		)

		self.neighbors_dict = {}
		for zone in self.neighbors.index:
			self.neighbors_dict[int(zone)] = dict(self.neighbors.loc[zone].dropna())

		return self.neighbors, self.neighbors_dict

	def get_input_bookings_filtered(self):

		self.bookings["hour"] = self.bookings.start_hour
		if "driving_distance" not in self.bookings.columns:
			self.bookings["driving_distance"] = self.bookings.euclidean_distance
		self.bookings["soc_delta"] = self.bookings["driving_distance"].apply(lambda x: get_soc_delta(x/1000))

		self.bookings["random_seconds_start"] = np.random.uniform(-600, 600, len(self.bookings))
		self.bookings["random_seconds_end"] = np.random.uniform(-600, 600, len(self.bookings))
		self.bookings["random_seconds_pos"] = np.random.uniform(0, 300, len(self.bookings))
		self.bookings.start_time = pd.to_datetime(self.bookings.start_time) + self.bookings.random_seconds_start.apply(
			lambda sec: datetime.timedelta(seconds=sec)
		)
		self.bookings.end_time = pd.to_datetime(self.bookings.end_time) + self.bookings.random_seconds_end.apply(
			lambda sec: datetime.timedelta(seconds=sec)
		)
		self.bookings.loc[self.bookings.start_time > self.bookings.end_time, "end_time"] = self.bookings.loc[
			self.bookings.start_time > self.bookings.end_time, "start_time"
		] + self.bookings.loc[self.bookings.start_time > self.bookings.end_time, "random_seconds_pos"].apply(
			lambda sec: datetime.timedelta(seconds=sec)
		)

		self.bookings["date"] = self.bookings.start_time.apply(lambda d: d.date())

		if self.data_source_id == "big_data_db":
			self.bookings.start_time = self.bookings.start_time - datetime.timedelta(hours=2)
			self.bookings.end_time = self.bookings.end_time - datetime.timedelta(hours=2)

		if self.city_name == "Minneapolis":
			tz = pytz.timezone("America/Chicago")
		elif self.city_name == "Torino":
			tz = pytz.timezone("Europe/Rome")

		now_utc = datetime.datetime.utcnow()
		now_local = pytz.utc.localize(now_utc, is_dst=None).astimezone(tz)
		self.bookings.start_time = self.bookings.start_time + now_local.utcoffset()
		self.bookings.end_time = self.bookings.end_time + now_local.utcoffset()
		self.bookings = pre_process_time(self.bookings)

		self.bookings = self.bookings.sort_values("start_time")
		self.bookings.loc[:, "ia_timeout"] = (
				self.bookings.start_time - self.bookings.start_time.shift()
		).apply(lambda x: x.total_seconds()).abs()
		self.bookings = self.bookings.loc[self.bookings.ia_timeout >= 0]
		self.bookings["avg_speed"] = (self.bookings["driving_distance"] / 1000) / (self.bookings["duration"] / 3600)

		#self.bookings = self.bookings[self.bookings.avg_speed < 30]
		#self.bookings = self.bookings[self.bookings.duration < 120 * 60]

		print(self.bookings[["driving_distance", "duration", "soc_delta", "avg_speed"]].describe())

		return self.bookings

	def get_hourly_ods(self):

		self.hourly_ods = {}

		for hour, hour_df in self.bookings.groupby("hour"):
			self.hourly_ods[hour] = pd.DataFrame(
				index=self.valid_zones,
				columns=self.valid_zones
			)
			hourly_od = pd.pivot_table(
				hour_df,
				values="start_time",
				index="origin_id",
				columns="destination_id",
				aggfunc=len,
				fill_value=0
			)
			self.hourly_ods[hour].loc[hourly_od.index, hourly_od.columns] = hourly_od
			self.hourly_ods[hour].fillna(0, inplace=True)

	def get_requests_rates(self):

		self.request_rates = {}

		for daytype, daytype_bookings_gdf in self.bookings.groupby("daytype"):
			self.request_rates[daytype] = {}
			for hour, hour_df in daytype_bookings_gdf.groupby("hour"):
				self.request_rates[daytype][hour] = hour_df.city.count() / (
					len(hour_df.day.unique())
				) / 3600

		self.avg_request_rate = pd.DataFrame(self.request_rates.values()).mean().mean()

		return self.request_rates

	def get_trip_kdes(self):

		self.trip_kdes = {}
		self.kde_columns = [
			"origin_id",
			"destination_id",
		]

		for daytype, daytype_bookings_gdf in self.bookings.groupby("daytype"):
			self.trip_kdes[daytype] = {}
			for hour, hour_df in daytype_bookings_gdf.groupby("hour"):
				self.trip_kdes[daytype][hour] = KernelDensity(
					bandwidth=self.kde_bw
				).fit(hour_df[self.kde_columns].dropna())

		return self.trip_kdes
