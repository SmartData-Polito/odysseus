import datetime

from sklearn.neighbors import KernelDensity

from odysseus.demand_modelling.demand_model import *
from odysseus.utils.bookings_utils import *
from odysseus.utils.time_utils import *
from odysseus.path_config.path_config import root_data_path


class PoissonKdeDemandModel(DemandModel):

    def __init__(
            self,
            city_name,
            data_source_id,
            demand_model_config,
            grid_crs
    ):

        super(PoissonKdeDemandModel, self).__init__(city_name, data_source_id, demand_model_config, grid_crs)

        self.request_rates = dict()
        self.avg_request_rate = -1
        self.trip_kdes = dict()
        self.grid_crs = grid_crs

        self.kde_bw = float(self.demand_model_config["kde_bandwidth"])

        self.norm_od_matrices_path = os.path.join(
            root_data_path, self.city_name, "norm", "od_matrices", self.data_source_id
        )

        with open(os.path.join(self.norm_od_matrices_path, "week_config.json"), "r") as f:
            self.week_config = json.load(f)

        self.week_slots = list(self.week_config["week_slots"].keys())
        for daytype in self.week_slots:
            daytype_trips_mask = self.bookings_train.start_time.dt.weekday.apply(
                lambda w: w in self.week_config["week_slots"][daytype]
            )
            self.bookings_train.loc[daytype_trips_mask, "daytype"] = daytype

    def get_requests_rates(self):

        for daytype, daytype_bookings_gdf in self.bookings_train.groupby("daytype"):
            self.request_rates[daytype] = {}
            for hour in range(24):
                hour_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
                self.request_rates[daytype][hour] = len(hour_df) / (
                    len(daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour].date.unique())
                ) / 3600
            for hour in range(24):
                hour_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
                if len(hour_df) == 0 or self.request_rates[daytype][hour] == 0:
                    rates = pd.Series(self.request_rates[daytype])
                    self.request_rates[daytype][hour] = rates[rates > 0].min()

        self.avg_request_rate = pd.DataFrame(self.request_rates.values()).mean().mean()

        return self.avg_request_rate, self.request_rates

    def get_trip_kdes(self):

        kde_columns = [
            "origin_i",
            "origin_j",
            "destination_i",
            "destination_j",
        ]
        self.trip_kdes = dict()
        for daytype, daytype_bookings_gdf in self.bookings_train.groupby("daytype"):
            self.trip_kdes[daytype] = {}
            for hour in range(24):
                slot_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
                if len(slot_df):
                    self.trip_kdes[daytype][hour] = KernelDensity(
                        bandwidth=self.kde_bw
                    ).fit(slot_df[kde_columns].dropna())
            # hours_list = list(range(7, 24)) + list(range(7))
            # for hour in hours_list:
            #     slot_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
            #     if len(slot_df) == 0:
            #         rates = pd.Series(self.request_rates[daytype])
            #         min_evaluable_rate = rates.idxmin()
            #         while min_evaluable_rate not in self.trip_kdes[daytype].keys():
            #             rates = rates.drop(min_evaluable_rate)
            #             min_evaluable_rate = rates.idxmin()
            #         self.trip_kdes[daytype][hour] = self.trip_kdes[daytype][min_evaluable_rate]

        return self.trip_kdes

    def fit_model(self):

        self.get_requests_rates()
        self.get_trip_kdes()

    def generate_booking_requests_list(self, start_datetime, end_datetime, requests_rate_factor):

        booking_requests_list = list()
        current_datetime = start_datetime
        current_hour = current_datetime.hour
        current_weekday = current_datetime.weekday()
        current_daytype = get_daytype_from_weekday(current_weekday)
        seconds_spent = 0

        while current_datetime < end_datetime:

            current_arrival_rate = self.request_rates[current_daytype][current_hour]
            current_trip_kde = self.trip_kdes[current_daytype][current_hour]

            timeout_sec = (
                np.random.exponential(
                    1 / (requests_rate_factor * current_arrival_rate)
                )
            )

            trip_sample = current_trip_kde.sample()
            origin_i = base_round(trip_sample[0][0], len(self.city_scenario.grid_matrix.index) - 1)
            origin_j = base_round(trip_sample[0][1], len(self.city_scenario.grid_matrix.columns) - 1)
            destination_i = base_round(trip_sample[0][2], len(self.city_scenario.grid_matrix.index) - 1)
            destination_j = base_round(trip_sample[0][3], len(self.city_scenario.grid_matrix.columns) - 1)

            o_id = self.city_scenario.grid_matrix.loc[origin_i, origin_j]
            d_id = self.city_scenario.grid_matrix.loc[destination_i, destination_j]
            booking_request = create_booking_request_dict(
                self.week_config, timeout_sec, current_datetime, o_id, d_id,
                self.avg_speed_kmh_mean, self.distance_matrix
            )
            booking_requests_list.append(booking_request)

            seconds_spent += timeout_sec
            current_datetime += datetime.timedelta(seconds=3600)
            current_hour = current_datetime.hour
            current_weekday = current_datetime.weekday()
            current_daytype = get_daytype_from_weekday(current_weekday)

        with open(os.path.join(self.demand_model_path, "booking_requests_list.json"), "w") as f:
            json.dump(booking_requests_list, f, sort_keys=True, indent=4)

        self.booking_requests_list = booking_requests_list
        return self.booking_requests_list

    def generate_booking_requests_sim(self, start_datetime, requests_rate_factor):

        weekday = start_datetime.weekday()
        daytype = get_daytype_from_week_config(self.week_config, weekday)
        hour = start_datetime.hour

        current_arrival_rate = self.request_rates[daytype][hour]
        current_trip_kde = self.trip_kdes[daytype][hour]

        timeout = (
            np.random.exponential(
                1 / requests_rate_factor / current_arrival_rate
            )
        )

        trip_sample = current_trip_kde.sample()

        origin_i = base_round(trip_sample[0][0], len(self.grid_matrix.index) - 1)
        origin_j = base_round(trip_sample[0][1], len(self.grid_matrix.columns) - 1)
        destination_i = base_round(trip_sample[0][2], len(self.grid_matrix.index) - 1)
        destination_j = base_round(trip_sample[0][3], len(self.grid_matrix.columns) - 1)
        origin_id = self.grid_matrix.loc[origin_i, origin_j]
        destination_id = self.grid_matrix.loc[destination_i, destination_j]
        origin_id = self.closest_valid_zone.loc[origin_id]
        destination_id = self.closest_valid_zone.loc[destination_id]

        booking_request_dict = create_booking_request_dict(
            self.week_config, timeout, start_datetime, origin_id, destination_id,
            self.avg_speed_kmh_mean * 5, self.distance_matrix
        )

        return [booking_request_dict]

    def save_results(self):

        self.save_config()

        with open(os.path.join(self.demand_model_path, "request_rates.pickle"), "wb") as f:
            pickle.dump(self.request_rates, f)
        with open(os.path.join(self.demand_model_path, "request_rates.json"), "w") as f:
            json.dump(self.request_rates, f, sort_keys=True, indent=4)

        with open(os.path.join(self.demand_model_path, "trip_kdes.pickle"), "wb") as f:
            pickle.dump(self.trip_kdes, f)


