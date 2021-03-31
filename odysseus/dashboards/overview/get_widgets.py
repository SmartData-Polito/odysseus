from datetime import date
import pytz
import streamlit as st

#from utils.legend_utils import *
#from dashboard.session_state import get

#session_state = get(password='', username='')



## Here will be listed the main menu widgets that affaect the dataframe took in consideration as a whole

last_day_list = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def load_slider_menu(year, month):

    start_date=date(year, month, 1)
    stop_date=date(year, month, last_day_list[month])
    inizio, fine = st.date_input("Choose start and end dates", [start_date, stop_date])
    # Is there a reason to choose slider over date input?
    #inizio, fine = st.slider("Choose start and end dates", min_value=start_date, max_value=stop_date, value=(start_date, stop_date))
    return inizio, fine


def load_time_menu(year, month):

    st_cols = st.beta_columns(4)

    time_period_type = st_cols[0].selectbox(
        'Tipo di periodo',
        ['Custom']
    )

    start_date = st_cols[1].date_input(
        'Data inizio:',
        datetime.datetime(year, month, 1, 0, 0, 0, tzinfo=pytz.utc)
    )
    end_date = st_cols[2].date_input(
        'Data fine:',
        datetime.datetime(year, month, 1, 0, 0, 0, tzinfo=pytz.utc)
    )

    if start_date > end_date:
        st.error('Error: End date must fall after start date.')

    agg_freqs = ["Giornaliera", "Settimanale", "Mensile"]
    agg_freq = st_cols[3].selectbox('Aggregazione:', agg_freqs, index=1)
    resampling_interval_dict = {"Oraria": "60Min", "Giornaliera": "1D", "Settimanale": "7D", "Mensile": "1M"}
    agg_freq_ = resampling_interval_dict[agg_freq]

    return agg_freq_, start_date, end_date



