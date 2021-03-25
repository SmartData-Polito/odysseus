import os, sys
import streamlit as st


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentparentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.append(parentparentdir)

from odysseus.dashboards.load_data import *
from odysseus.dashboards.overview.get_widgets import *
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
def get_bookings_count_plot_data(city_chosen,year_chosen,month_chosen,source_chosen):
    city = str(city_chosen)
    year = str(year_chosen)
    month = str(month_chosen)
    data_source_id = str(source_chosen)

    origins, destinations = load_origin_destination_data(city, year, month, data_source_id ) 

    return origins, destinations
