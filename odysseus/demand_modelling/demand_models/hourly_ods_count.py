import datetime

from odysseus.demand_modelling.demand_model import *
from odysseus.utils.time_utils import *


class HourlyODsCountDemandModel(DemandModel):

    def __init__(
            self,
            city_name,
            data_source_id,
            demand_model_config
    ):
        super(HourlyODsCountDemandModel, self).__init__(city_name, data_source_id, demand_model_config)
        self.od_matrices = dict()

    def fit_model(self):

        for daytype, daytype_bookings_gdf in self.bookings_train.groupby("daytype"):
            self.od_matrices[daytype] = {}
            for hour in range(24):
                hour_df = daytype_bookings_gdf[daytype_bookings_gdf.start_hour == hour]
                self.od_matrices[daytype][hour] = pd.DataFrame(
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
                self.od_matrices[daytype][hour].loc[hourly_od.index, hourly_od.columns] = hourly_od
                self.od_matrices[daytype][hour].fillna(0, inplace=True)
                self.od_matrices[daytype][hour].sort_index(axis=0, inplace=True)
                self.od_matrices[daytype][hour].sort_index(axis=1, inplace=True)

    def generate_booking_requests_list(self, start_datetime, end_datetime):
        booking_requests_list = list()
        current_datetime = start_datetime
        current_hour = current_datetime.hour
        current_weekday = current_datetime.weekday()
        current_daytype = get_daytype_from_weekday(current_weekday)
        seconds_spent = 0
        while current_datetime < end_datetime:
            for o_id in self.od_matrices[current_daytype][current_hour].index:
                for d_id in self.od_matrices[current_daytype][current_hour].columns:
                    n_bookings_to_generate = self.od_matrices[current_daytype][current_hour].loc[o_id, d_id]
                    if n_bookings_to_generate:
                        timeout_sec = 3600 / n_bookings_to_generate
                        for booking_request_to_generate in range(n_bookings_to_generate):
                            booking_request = create_booking_request_dict(timeout_sec, current_datetime, o_id, d_id)
                            booking_requests_list.append(booking_request)
                            seconds_spent += timeout_sec
            current_datetime += datetime.timedelta(seconds=3600)
            current_hour = current_datetime.hour
            current_weekday = current_datetime.weekday()
            current_daytype = get_daytype_from_weekday(current_weekday)

        self.booking_requests_list = booking_requests_list
        return self.booking_requests_list

    def save_results(self):

        self.save_config()

        with open(os.path.join(self.demand_model_path, "booking_requests_list.json"), "w") as f:
            json.dump(self.booking_requests_list, f, sort_keys=True, indent=4, default=str)

        for daytype in self.od_matrices.keys():
            daytype_writer = pd.ExcelWriter(
                os.path.join(self.demand_model_path, "_".join([daytype, "od_matrices.xlsx"])),
            )
            for hour in range(24):
                self.od_matrices[daytype][hour].to_excel(
                    daytype_writer, sheet_name="_".join([daytype, str(hour)])
                )
            daytype_writer.save()

        with open(os.path.join(self.demand_model_path, "od_matrices.pickle"), "wb") as f:
            pickle.dump(self.od_matrices, f)