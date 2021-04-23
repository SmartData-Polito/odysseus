from odysseus.dashboards.dashboard_field.dashboard_chart import DashboardChart
from odysseus.dashboards.dashboard_field.utils import st_functional_columns

from threading import Thread


import streamlit as st
from functools import partial
import pandas as pd
import builtins
import plotly.express as px

import folium
from folium import plugins
from folium.plugins import HeatMap
from folium.plugins import HeatMapWithTime

import datetime 
from streamlit_folium import folium_static

class ChartMap(DashboardChart, Thread):

    def __init__(self, data, title, subtitle, tipo="heatmap", parametro='Torino'):
        
        Thread.__init__(self)
        DashboardChart.__init__(self, title, name=title, subtitle=subtitle)
        self.data = data
        self.parametro=parametro
        self.tipo = tipo
        
#        min = datetime.datetime.fromisoformat(str(self.data['start_time'].min()))
#        max = datetime.datetime.fromisoformat(str(self.data['start_time'].max()))

#        args = [["slider", "Va che bello questo slider", min, max, (min, max)]]
#        self.widget_list = [partial(st_functional_columns, args)]

    def get_heatmap(self):
        
        data = self.data

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
        _map = folium.Map(location=locations[self.parametro],
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

    def get_heatmapWithTime(self):

        data = self.data
        data['hour']=data['datetime'].apply(lambda x: x.hour)
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

        _map = folium.Map(location=locations[self.parametro],
                        tiles='Stamen Toner', 
                        zoom_start = 12) 
    
        # Ensure you're handing it floats

        # Filter the DF for rows, then columns, then remove NaNs
        heat_df = data[['hour','lat','lng']]
        heat_df = heat_df.dropna(axis=0, subset=['hour','lat','lng'])

        lat_long_list = []
        for i in range(0,24):
            temp=[]
            for index, instance in heat_df[heat_df['hour'] == i].iterrows():
                temp.append([instance['lat'],instance['lng']])
            lat_long_list.append(temp)


        HeatMapWithTime(lat_long_list,radius=5,auto_play=True,position='bottomright').add_to(_map)

        return _map


    def show_heatmap(self):
        with st.spinner("Sto creando la heatmap..."):
            fig = self.get_heatmap()
        self.show_heading()
        folium_static(fig)

    def show_heatmapWithTime(self):
        
        with st.spinner("Sto creando la heatmap temporale..."):
            fig = self.get_heatmapWithTime()
        self.show_heading()
        folium_static(fig)

    def run(self):
        print ("Thread '" + self.tipo + "' avviato")
        if (self.tipo == "heatmap"):
            self.show_heatmap()
        else:
            self.show_heatmapWithTime()
        
        print ("Thread '" + self.name + "' terminato")