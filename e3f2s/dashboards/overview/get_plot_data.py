import os, sys
import streamlit as st
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentparentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.append(parentparentdir)

from e3f2s.dashboards.load_data import *
from e3f2s.dashboards.overview.get_widgets import *
import plotly.express as px

@st.cache(allow_output_mutation=True)
def plot_df(df, agg_freq_, count_col):

    df['start_time'] = pd.to_datetime(df['start_time'], utc=True)
    plot_df = df[["start_time", count_col]].set_index("start_time").resample(
        agg_freq_
    ).count().asfreq(agg_freq_, fill_value=0)
    fig = px.line(plot_df)

    return fig

@st.cache(allow_output_mutation=True)
def get_bookings_count_plot_data():

    # agg_freq_, start_date, end_date = load_time_menu()

    #start_date, end_date = load_slider_menu()
    # here it should call the function load_bookig_by_hour from load_data.py
    data_source_id = "big_data_db"
    city="Torino"
    year = 2017
    month=12
    #bookings_by_hour = load_bookings_by_hour(club_id, start_date, end_date)
    origins, destinations = load_origin_destination_data(city, data_source_id, year, month ) #citta,sorgente,anno,mese  

    #deleted_bookings_by_hour = load_deleted_bookings_by_hour(club_id, start_date, end_date)

    # club_facility_filter, club_activity_filter, age_filter, sex_filter = load_filters_menu(bookings_by_hour)

    # if club_facility_filter != 'Tutte':
    #     bookings_by_hour = bookings_by_hour[bookings_by_hour.club_facility_name == club_facility_filter]

    # if club_activity_filter != 'Tutte':
    #     bookings_by_hour = bookings_by_hour[bookings_by_hour.club_activity_name == club_activity_filter]

    # if not len(bookings_by_hour):

    #     st.error(
    #         """
    #         Sembra che non ci siano prenotazioni con i filtri richiesti!
    #         """
    #     )
    #     return bookings_by_hour, None, None, None

    # else:

    #     if age_filter != 'Tutte' and sex_filter != 'Tutti':
    #         col_filter = "_".join([sex_filter, age_filter])
    #         bookings_count = load_plot_df(bookings_by_hour, agg_freq_, col_filter)
    #         deleted_bookings_count = load_plot_df(deleted_bookings_by_hour, agg_freq_, col_filter)
    #         count_col = col_filter
    #     if age_filter != 'Tutte' and sex_filter == 'Tutti':
    #         bookings_count = load_plot_df(bookings_by_hour, agg_freq_, age_filter)
    #         deleted_bookings_count = load_plot_df(deleted_bookings_by_hour, agg_freq_, age_filter)
    #         count_col = age_filter
    #     if age_filter == 'Tutte' and sex_filter != 'Tutti':
    #         bookings_count = load_plot_df(bookings_by_hour, agg_freq_, sex_filter)
    #         deleted_bookings_count = load_plot_df(deleted_bookings_by_hour, agg_freq_, sex_filter)
    #         count_col = sex_filter
    #     if age_filter == 'Tutte' and sex_filter == 'Tutti':
    #         bookings_count = load_plot_df(bookings_by_hour, agg_freq_, "bookings_count")
    #         deleted_bookings_count = load_plot_df(deleted_bookings_by_hour, agg_freq_, "bookings_count")
    #         count_col = "bookings_count"

    #     bubble_plot_df = load_plot_df(bookings_by_hour, "60Min", count_col)
    #     bubble_plot_df["datetime"] = pd.to_datetime(bubble_plot_df.index.values)
    #     bubble_plot_df["weekday"] = bubble_plot_df.datetime.apply(lambda dt: dt.weekday())
    #     bubble_plot_df["hour"] = bubble_plot_df.datetime.apply(lambda dt: dt.hour)

    return origins, destinations#, bookings_count, deleted_bookings_count, bubble_plot_df
