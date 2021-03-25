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
    inizio, fine = st.slider("Choose start and end dates", min_value=start_date, max_value=stop_date, value=(start_date, stop_date))
    return inizio, fine


