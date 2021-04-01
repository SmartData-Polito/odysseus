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

@st.cache(allow_output_mutation=True)
def get_bookings_map(city, data, od):
    if od =='origin':
        data = data.rename(columns={'start_latitude':'lat', 'start_longitude':'lng', 'start_time':'datetime'})
    else:
        data = data.rename(columns={'end_latitude':'lat', 'end_longitude':'lng', 'end_time':'datetime'})

    locations = {
    "Torino": [45.0781, 7.6761],
    "Amsterdam": [52.3676, 4.9041],
    "Austin": [30.2672, -97.7431],
    "Berlin": [52.5200, 13.4050],
    "Calgary": [51.0447, -114.0719],
    "Columbus": [39.9612, -82.9988],
    "Denver": [39.7392, -104.9903],
    "Firenze": [43.7696, 11.2558],
    "Frankfurt": [50.1109, 8.6821],
    "Hamburg": [53.5511, 9.9937]
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

@st.cache(allow_output_mutation=True)
def get_bookings_by_hour(city,data,start_date,end_date,data_source_id,od="origins"):
    start_year = start_date.year
    start_month = start_date.month
    end_year = start_date.year
    end_month = start_date.month

    if od == "origins":
        df,_ = load_origin_destination_data(city, start_year, start_month, data_source_id)
        filtro = "start_hour"
    else:
        _,df = load_origin_destination_data(city, start_year, start_month, data_source_id)
        filtro = "end_hour"

    df_busy = df.filter([filtro], axis=1)
    df_busy["occurance"] = 1
    most_busy_hour = df_busy.groupby(by=filtro).sum(["occurance"]).sort_values(by=["occurance"], ascending=[True])
    most_busy_hour = most_busy_hour.reset_index()
    return  px.bar(most_busy_hour, x=filtro, y='occurance')

@st.cache(allow_output_mutation=True)
def get_most_used_cars(city,data,start_date,end_date,data_source_id):
    start_year = start_date.year
    start_month = start_date.month
    end_year = start_date.year
    end_month = start_date.month

    df,_ = load_origin_destination_data(city, start_year, start_month, data_source_id)

    df_plates = pd.DataFrame()
    df_plates["plate"]=df.plate#filter(["plate"], axis=1)
    df_plates["occurance"] = 1
    most_used = df_plates.groupby(by="plate").sum(["occurance"]).sort_values(by=["occurance"], ascending=[False]).head(10)
    most_used = most_used.reset_index()

    return  px.bar(most_used, x="occurance", y='plate',orientation='h')



@st.cache(allow_output_mutation=True)
def get_average_duration(city,data,start_date,end_date,data_source_id):
    start_year = start_date.year
    start_month = start_date.month

    df,_ = load_origin_destination_data(city, start_year, start_month, data_source_id)
    filtro = "start_hour"
    
    df_duration = df.filter([filtro,"duration"], axis=1)
    avg_duration = df_duration.groupby(by=filtro).mean(["duration"]).sort_values(by=[filtro], ascending=[True])
    avg_duration = avg_duration.reset_index()


    fig = px.bar(avg_duration, x=filtro, y="duration")

    fig.update_layout(
    title="Average Duration of Trips by Start Hour",
    xaxis_title="Hours",
    yaxis_title="Average Time",
    # legend_title="Legend Title",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="White"
        )
    )

    return fig