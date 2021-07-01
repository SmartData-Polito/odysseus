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
import branca.colormap
from collections import defaultdict

import datetime 
from streamlit_folium import folium_static

class ChartMap(DashboardChart, Thread):

    def __init__(self, og_data, title, subtitle, grid, start, end, tipo="heatmap", parametro='Torino'):
        
        Thread.__init__(self)
        DashboardChart.__init__(self, title, name=title, subtitle=subtitle)
        self.og_data = og_data
        #self.dest_data = dest_data
        self.parametro=parametro
        self.tipo = tipo
        self.grid = grid
        st.write(grid)
        
        self.startDay = start
        self.endDay = end
        arg = [["selectbox", "Scegli grafico", ['out_flow_count', 'in_flow_count','origin_count']]]

        self.widget_list= [partial(st_functional_columns, arg)]


    def get_choropleth_mapbox(self, column):

        # aaa = self.og_data.loc[self.startDay:self.endDay]
        data_to_show = column
        plot_df = self.og_data.loc[self.og_data['date'] == '2017-10-09']
        fig = px.choropleth_mapbox(plot_df,
                                geojson=self.grid,
                                locations=plot_df.tile_ID,
                                color=data_to_show,
                                color_continuous_scale="YlOrRd",
                                opacity=0.7,
                                center={"lat": 45.06, "lon":7.67},
                                mapbox_style="open-street-map",
                                zoom=11)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return fig


    def show_choropleth_mapbox(self):
        self.show_heading()
        stat_column,= self.show_widgets()[0]
        fig = self.get_choropleth_mapbox(stat_column)
        st.plotly_chart(fig, use_container_width=True)



    def get_heatmap(self):
        
        data_og = self.og_data
        #data_dest = self.dest_data

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
                        zoom_start = 11) 
    
        og_points = data_og[['lat','lng']]
        og_points = og_points.dropna(axis=0, subset=['lat','lng'])
        heat_og = [[row["lat"], row["lng"]] for index, row in og_points.iterrows()]
        
        """ dest_points = data_dest[['end_lat','end_long']]
        dest_points = dest_points.dropna(axis=0, subset=['end_lat','end_long'])
        heat_dest = [[row["end_lat"], row["end_long"]] for index, row in dest_points.iterrows()] """

        steps=20
        colormap = branca.colormap.linear.YlOrRd_09.scale(0, 1).to_step(steps)
        gradient_map=defaultdict(dict)
        for i in range(steps):
            gradient_map[1/steps*i] = colormap.rgb_hex_str(1/steps*i)
        colormap.add_to(_map)

        HeatMap(heat_og, radius=17).add_to(_map)
        #HeatMap(heat_dest, radius=17).add_to(_map)
        return _map

    def get_heatmapWithTime(self):

        data = self.og_data
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
    
        heat_df = data[['hour','lat','lng']]
        heat_df = heat_df.dropna(axis=0, subset=['hour','lat','lng'])

        lat_long_list = []
        for i in range(0,24):
            temp=[]
            for index, instance in heat_df[heat_df['hour'] == i].iterrows():
                temp.append([instance['lat'],instance['lng']])
            lat_long_list.append(temp)


        HeatMapWithTime(lat_long_list,radius=7,auto_play=True, position='bottomright').add_to(_map)

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