from datetime import date
import pytz
import streamlit as st

#from utils.legend_utils import *
#from dashboard.session_state import get

#session_state = get(password='', username='')

last_day_list = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def load_slider_menu(year, month):

    start_date=date(year, month, 1)
    stop_date=date(year, month, last_day_list[month])
    inizio, fine = st.slider("Seleziona la data", min_value=start_date, max_value=stop_date, value=(start_date, stop_date))
    return inizio, fine


def load_time_menu():

    st_cols = st.beta_columns(4)

    time_period_type = st_cols[0].selectbox(
        'Tipo di periodo',
        ['Custom']
    )

    start_date = st_cols[1].date_input(
        'Data inizio:',
        datetime.datetime(2015, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
    )
    end_date = st_cols[2].date_input(
        'Data fine:',
        datetime.datetime(2021, 4, 1, 0, 0, 0, tzinfo=pytz.utc)
    )

    if start_date > end_date:
        st.error('Error: End date must fall after start date.')

    agg_freqs = ["Giornaliera", "Settimanale", "Mensile"]
    agg_freq = st_cols[3].selectbox('Aggregazione:', agg_freqs, index=1)
    resampling_interval_dict = {"Oraria": "60Min", "Giornaliera": "1D", "Settimanale": "7D", "Mensile": "1M"}
    agg_freq_ = resampling_interval_dict[agg_freq]

    return agg_freq_, start_date, end_date


def load_filters_menu(bookings_by_hour_):

    st_cols = st.beta_columns(4)

    club_facility_filter = st_cols[0].selectbox(
        'Struttura',
        ['Tutte'] + list(bookings_by_hour_.club_facility_name.unique())
    )
    club_activity_filter = st_cols[1].selectbox(
        'Attività',
        ['Tutte'] + list(bookings_by_hour_.club_activity_name.unique())
    )
    age_filter = st_cols[2].selectbox(
        'Età',
        ['Tutte'] + age_bin_cols
    )
    sex_filter = st_cols[3].selectbox(
        'Sesso',
        ['Tutti', "male", "female", "sex_unknown"] 
    )

    return club_facility_filter, club_activity_filter, age_filter, sex_filter


# def load_bookings_count_widgets(st_obj):

#     chart_style = st_obj.selectbox(
#         'Stile del grafico:',
#         ["Linea", "Barre"]
#     )
#     chart_style_dict = {
#         "Linea": "line", "Barre": "bar",
#     }
#     chart_style_ = chart_style_dict[chart_style]

#     return chart_style_
