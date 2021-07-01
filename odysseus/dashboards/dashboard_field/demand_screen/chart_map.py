from odysseus.dashboards.dashboard_field.dashboard_chart import DashboardChart
from odysseus.dashboards.dashboard_field.utils import st_functional_columns

from odysseus.dashboards import session_state as SessionState
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
from streamlit_plotly_events import plotly_events
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

        # aaa = self.og_data.loc[self.startDay:self.endDay]
        data_to_show = column
        plot_df = self.og_data#.loc[self.og_data['date'] == '2017-10-09']
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

    def get_map(self):
        fig = px.choropleth_mapbox(self.og_data,
                                geojson=self.grid,
                                locations=self.og_data.tile_ID,
                                #color="zone_id",
                                opacity=0.5,
                                center={"lat": 45.06, "lon":7.67},
                                mapbox_style="open-street-map",
                                zoom=11)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.update(layout_coloraxis_showscale=False)
        return fig




    def show_prova5(self):
        self.show_heading()
        column,= self.show_widgets()[0]
        scelta = SessionState.get( zone = None)
        if scelta.zone is None or st.button("Seleziona la zona"):
            st.title("Premi su una cella per vedere i dati relativi a quella zona")

            fig = self.get_map()

            a = plotly_events(fig, hover_event=False, override_width=1000, select_event=False)
            if a == []:
                scelta.zone = None
                st.stop()
            else:
                scelta.zone = a
                st.experimental_rerun()
        sq_choice = self.og_data.loc[scelta.zone[0]["pointNumber"]].tile_ID
        line_plot = self.og_data.loc[self.og_data['tile_ID'] == sq_choice]
        line_plot = line_plot.set_index('date').resample(
                    '1D'
                ).sum().asfreq('1D', fill_value=0)

        plot_df = line_plot[column]
        fig = px.bar(plot_df)
        fig.update_layout(
            xaxis_title="Time series",
            yaxis_title="---",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="MediumSlateBlue"
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    def run(self):
        print ("Thread '" + self.tipo + "' avviato")
        if (self.tipo == "heatmap"):
            self.show_heatmap()
        else:
            self.show_heatmapWithTime()
        
        print ("Thread '" + self.name + "' terminato")