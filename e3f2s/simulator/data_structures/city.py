import datetime
import pytz
import math

from sklearn.neighbors import KernelDensity

from e3f2s.utils.geospatial_utils import *

from e3f2s.simulator.loading.loader import Loader
from e3f2s.utils.vehicle_utils import *
from e3f2s.utils.time_utils import *


class City:

    def __init__(self, city_name, data_source_id, sim_general_conf, kde_bw=1):

        self.city_name = city_name

        if self.city_name == "Torino":
            self.tz = pytz.timezone("Europe/Rome")
        elif self.city_name == "Berlin":
            self.tz = pytz.timezone("Europe/Berlin")
        elif self.city_name == "Minneapolis":
            self.tz = pytz.timezone("America/Chicago")
        elif self.city_name == "Louisville":
            self.tz = pytz.timezone("America/Kentucky/Louisville")

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

        self.bookings.start_time = pd.to_datetime(self.bookings.start_time).dt.tz_convert(self.tz)
        self.bookings.end_time = pd.to_datetime(self.bookings.end_time).dt.tz_convert(self.tz)
        self.bookings["date"] = self.bookings.start_time.apply(lambda d: d.date())
        self.bookings["daytype"] = self.bookings.start_daytype
        self.bookings["city"] = self.city_name

        self.grid = self.get_squared_grid()
        self.grid_matrix = get_city_grid_as_matrix(
            self.locations,
            self.bin_side_length
        )
        self.grid["zone_id"] = self.grid.index.values
        self.map_zones_on_trips(self.grid)
        self.bookings = self.get_input_bookings_filtered().dropna()
        self.bookings = self.bookings.loc[
            (self.bookings.origin_id.isin(self.grid.index)) & (
                self.bookings.destination_id.isin(self.grid.index)
            )
        ]

        self.valid_zones = self.get_valid_zones()

        self.neighbors_dict = self.get_neighbors_dicts()
        self.request_rates = self.get_requests_rates()
        self.trip_kdes = self.get_trip_kdes()

    def get_squared_grid (self):

        self.locations = pd.concat([
            self.trips_origins.geometry, self.trips_destinations.geometry
        ], ignore_index=True)
        self.locations.crs = "epsg:4326"
        squared_grid = get_city_grid_as_gdf(
            self.locations,
            self.bin_side_length * 1.4
        )
        return squared_grid

    def map_zones_on_trips(self, zones):
        self.trips_origins = gpd.sjoin(
            zones,
            self.trips_origins,
            how='right',
            op='contains'
        )
        self.trips_destinations = gpd.sjoin(
            zones,
            self.trips_destinations,
            how='right',
            op='contains'
        )
        self.bookings["origin_id"] = self.trips_origins.zone_id
        self.bookings["destination_id"] = self.trips_destinations.zone_id

    def get_input_bookings_filtered(self):

        self.bookings = self.bookings.sort_values("start_time")

        if "driving_distance" not in self.bookings.columns:
            self.bookings["driving_distance"] = self.bookings.euclidean_distance
        self.bookings["soc_delta"] = self.bookings["driving_distance"].apply(lambda x: get_soc_delta(x / 1000))

        self.bookings["random_seconds_start"] = np.random.uniform(-900, 900, len(self.bookings))
        self.bookings.start_time = pd.to_datetime(self.bookings.start_time) + self.bookings.random_seconds_start.apply(
            lambda sec: datetime.timedelta(seconds=sec)
        )
        self.bookings = get_time_group_columns(self.bookings)
        self.bookings["hour"] = self.bookings.start_hour
        self.bookings["daytype"] = self.bookings.start_daytype
        self.bookings["date"] = self.bookings.start_time.apply(lambda d: d.date())

        if "duration" not in self.bookings.columns:
            self.bookings["random_seconds_end"] = np.random.uniform(-900, 900, len(self.bookings))
            self.bookings["random_seconds_pos"] = np.random.uniform(0, 450, len(self.bookings))

            self.bookings.end_time = pd.to_datetime(self.bookings.end_time) + self.bookings.random_seconds_end.apply(
                lambda sec: datetime.timedelta(seconds=sec)
            )
            self.bookings.loc[self.bookings.start_time > self.bookings.end_time, "end_time"] = self.bookings.loc[
                self.bookings.start_time > self.bookings.end_time, "start_time"
            ] + self.bookings.loc[self.bookings.start_time > self.bookings.end_time, "random_seconds_pos"].apply(
                lambda sec: datetime.timedelta(seconds=sec)
            )
            self.bookings.loc[:, "duration"] = (
                    self.bookings.end_time - self.bookings.start_time
            ).apply(lambda x: x.total_seconds())
        else:
            self.bookings.end_time = pd.to_datetime(self.bookings.end_time) + self.bookings.duration.apply(
                lambda sec: datetime.timedelta(seconds=abs(sec))
            )

        self.bookings.loc[:, "ia_timeout"] = (
                self.bookings.start_time - self.bookings.start_time.shift()
        ).apply(lambda x: x.total_seconds()).abs()
        self.bookings = self.bookings.loc[self.bookings.ia_timeout >= 0]

        self.bookings = self.bookings[self.bookings.duration > 0]
        self.bookings = self.bookings[self.bookings.driving_distance >= 0]
        self.bookings.loc[self.bookings.driving_distance == 0, "driving_distance"] = self.bin_side_length
        self.bookings["soc_delta"] = self.bookings["driving_distance"].apply(
            lambda x: get_soc_delta(x / 1000)
        )
        self.bookings["avg_speed"] = self.bookings["driving_distance"] / self.bookings["duration"]
        self.bookings["avg_speed_kmh"] = self.bookings.avg_speed * 3.6

        if self.city_name in ["Minneapolis", "Louisville"]:
            self.bookings = self.bookings[self.bookings.avg_speed_kmh < 30]
        elif self.city_name in ["Torino", "Berlin"]:
            self.bookings = self.bookings[self.bookings.avg_speed_kmh < 120]
            self.bookings = self.bookings[
                (self.bookings.duration > 3*60) & (
                    self.bookings.duration < 60*60
                ) & (
                    self.bookings.euclidean_distance > 500
                )
            ]

        return self.bookings

    def get_valid_zones(self, count_threshold=0):

        self.valid_zones = self.bookings.origin_id.value_counts().sort_values().tail(
            int(self.sim_general_conf["k_zones_factor"] * len(self.grid))
        ).index

        origin_zones_count = self.bookings.origin_id.value_counts()
        dest_zones_count = self.bookings.destination_id.value_counts()

        valid_origin_zones = origin_zones_count[(origin_zones_count > count_threshold)]
        valid_dest_zones = dest_zones_count[(dest_zones_count > count_threshold)]

        self.valid_zones = self.valid_zones.intersection(
            valid_origin_zones.index.intersection(
                valid_dest_zones.index
            ).astype(int)
        )
        return self.valid_zones

    def get_neighbors_dicts(self):

        self.neighbors_dict = {}
        for i in self.grid_matrix.index:
            for j in self.grid_matrix.columns:
                zone = self.grid_matrix.iloc[i, j]
                i_low = i-1 if i-1 >= 0 else 0
                i_up = i+1 if i+1 < len(self.grid_matrix.index) else len(self.grid_matrix.index) - 1
                j_low = j-1 if j-1 >= 0 else 0
                j_up = j+1 if j+1 < len(self.grid_matrix.columns) else len(self.grid_matrix.columns) - 1
                iii = 0
                self.neighbors_dict[int(zone)] = {}
                for ii in range(i_low, i_up+1):
                    for jj in range(j_low, j_up+1):
                        if ii != i or jj != j and self.grid_matrix.iloc[ii, jj] in self.grid.index:
                            self.neighbors_dict[int(zone)].update({iii: self.grid_matrix.iloc[ii, jj]})
                            iii += 1
        return self.neighbors_dict

    def get_hourly_ods(self):

        self.hourly_ods = {}

        for hour, hour_df in self.bookings.groupby("hour"):
            self.hourly_ods[hour] = pd.DataFrame(
                index=self.grid.index,
                columns=self.grid.index
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
            for hour in range(24):
                hour_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
                self.request_rates[daytype][hour] = hour_df.city.count() / (
                    len(daytype_bookings_gdf.date.unique())
                ) / 3600
            for hour in range(24):
                hour_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
                if len(hour_df) == 0 or self.request_rates[daytype][hour] == 0:
                    rates = pd.Series(self.request_rates[daytype])
                    self.request_rates[daytype][hour] = rates[rates > 0].min()

        self.avg_request_rate = pd.DataFrame(self.request_rates.values()).mean().mean()

        return self.request_rates

    def get_trip_kdes(self):

        for i in self.grid_matrix.index:
            for j in self.grid_matrix.columns:
                zone = self.grid_matrix.iloc[i, j]
                self.bookings.loc[self.bookings.origin_id == zone, "origin_i"] = i
                self.bookings.loc[self.bookings.origin_id == zone, "origin_j"] = j
                self.bookings.loc[self.bookings.destination_id == zone, "destination_i"] = i
                self.bookings.loc[self.bookings.destination_id == zone, "destination_j"] = j

        self.trip_kdes = {}
        self.kde_columns = [
            "origin_i",
            "origin_j",
            "destination_i",
            "destination_j",
        ]

        for daytype, daytype_bookings_gdf in self.bookings.groupby("daytype"):
            self.trip_kdes[daytype] = {}
            for hour in range(24):
                hour_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
                if len(hour_df):
                    self.trip_kdes[daytype][hour] = KernelDensity(
                        bandwidth=self.kde_bw
                    ).fit(hour_df[self.kde_columns].dropna())
            hours_list = list(range(7, 24)) + list(range(7))
            for hour in hours_list:
                hour_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
                if len(hour_df) == 0:
                    rates = pd.Series(self.request_rates[daytype])
                    self.trip_kdes[daytype][hour] = self.trip_kdes[daytype][rates.idxmin()]

        return self.trip_kdes
