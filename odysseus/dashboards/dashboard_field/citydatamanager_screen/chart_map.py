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
        
        self.startDay = start
        self.endDay = end
        arg = [["selectbox", "Scegli grafico", ['out_flow_count', 'in_flow_count','origin_count']]]

        self.widget_list= [partial(st_functional_columns, arg)]


    def get_choropleth_mapbox(self, column):

        data_to_show = column
        plot_df = self.og_data.loc[(self.og_data['date'] > str(self.startDay)) & (self.og_data['date'] < str(self.endDay))]
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


