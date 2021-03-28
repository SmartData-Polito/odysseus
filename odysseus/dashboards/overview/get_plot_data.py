import os, sys
import streamlit as st


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentparentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.append(parentparentdir)

from odysseus.dashboards.load_data import *
from odysseus.dashboards.overview.get_widgets import *
import plotly.express as px

import folium
from folium import plugins
from folium.plugins import HeatMap

@st.cache(allow_output_mutation=True)
def plot_df(df, agg_freq_, count_col):
    if 'start_time' in df.columns:
        time_col='start_time'
    else:
        time_col = 'end_time' 
    
    df[time_col] = pd.to_datetime(df[time_col], utc=True)
    
    plot_df = df[[time_col, count_col]].set_index(time_col).resample(
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

    fig_origins = plot_df(origins, "60Min", 'plate')
    fig_destinations = plot_df(origins, "60Min", 'plate')

    return fig_origins, fig_destinations

def get_bookings_map(city, data, od):
    if od =='origin':
        data = data.rename(columns={'start_latitude':'lat', 'start_longitude':'lng', 'start_time':'datetime'})
    else:
        data = data.rename(columns={'end_latitude':'lat', 'end_longitude':'lng', 'end_time':'datetime'})

    locations = {
    "Torino": [45.0781, 7.6761]
    }
    """ 
    _map = folium.Map(location=locations[city],
        tiles='Stamen Toner', zoom_start=12)

    data.apply(lambda row:folium.Marker(location=[row["lat"], row["lng"]]).add_to(_map),
            axis=1)
"""
    _map = folium.Map(location=locations[city],
                    zoom_start = 12) 
 
    # Ensure you're handing it floats

    # Filter the DF for rows, then columns, then remove NaNs
    heat_df = data[['lat','lng']]
    heat_df = heat_df.dropna(axis=0, subset=['lat','lng'])

    # List comprehension to make out list of lists
    heat_data = [[row["lat"], row["lng"]] for index, row in heat_df.iterrows()]

    # Plot it on the map
    HeatMap(heat_data).add_to(_map)

    return _map
