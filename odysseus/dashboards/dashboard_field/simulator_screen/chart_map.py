from odysseus.dashboards.dashboard_field.dashboard_chart import DashboardChart
from odysseus.dashboards.dashboard_field.utils import st_functional_columns

from threading import Thread


import streamlit as st
from functools import partial
import plotly.express as px


class ChartMap(DashboardChart):

    def __init__(self, data, title, subtitle, parametro='Torino'):
        
        DashboardChart.__init__(self, title, name=title, subtitle=subtitle)
        self.data = data
        self.parametro=parametro
        param_list = list(self.data.columns.difference(['zone_id', 'zone_id_or', 'charge_n_1', 'geometry']))

        arg = [["selectbox", "Scegli grafico", param_list]]

        self.widget_list= [partial(st_functional_columns, arg)]


    def get_choropleth_mapbox(self, column):

        data_to_show = column
        plot_df = self.data
        fig = px.choropleth_mapbox(plot_df,
                                geojson=plot_df.geometry,
                                locations=plot_df.zone_id_or,
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
