from odysseus.dashboards.dashboard_field.dashboard_chart import DashboardChart
from odysseus.dashboards.dashboard_field.utils import st_functional_columns

import streamlit as st
from functools import partial
import pandas as pd
import datetime

import plotly.express as px


class ChartTemp(DashboardChart):

    def __init__(self, data, title, subtitle, tipo="Altair", parametro='plate'):
        super().__init__(title, name=title, subtitle=subtitle)
        self.data = data
        self.parametro=parametro
        self.tipo = tipo


        min = datetime.datetime.fromisoformat(str(self.data['start_time'].min()))
        max = datetime.datetime.fromisoformat(str(self.data['start_time'].max()))
        arg = [[    "selectbox", "Scegli il parametro", ['plate']], 
                ["selectbox", "Scegli aggregazione", ["60Min", "2H", "1D"]]]

        self.widget_list= [partial(st_functional_columns, arg)]

    @st.cache
    def get_bookings_count(self, count_col, agg_freq_):

        #self.show_heading()
        #self.data.plot_dashboard_st(type=self.parametro, regione=self.regione, tipo=self.tipo)
        df = self.data
        plot_df = df[['start_time', count_col]].set_index('start_time').resample(
            agg_freq_
        ).count().asfreq(agg_freq_, fill_value=0)
        fig = px.line(plot_df)

        return fig

        #st.plotly_chart(fig, use_container_width=True)

    @st.cache
    def get_bookings_by_hour(self):

        #self.show_heading()
        filtro = "start_hour"

        df_busy = self.data.filter([filtro], axis=1)
        df_busy["occurance"] = 1
        most_busy_hour = df_busy.groupby(by=filtro).sum(["occurance"]).sort_values(by=["occurance"], ascending=[True])
        most_busy_hour = most_busy_hour.reset_index()
        fig = px.bar(most_busy_hour, x=filtro, y='occurance')

        return fig

        #st.plotly_chart(fig, use_container_width=True)


    @st.cache
    def get_bubble_plot(self):

        #self.show_heading()
        df = self.data
        df = df.groupby(['start_weekday','start_hour']).size().to_frame('counts').reset_index()
        fig = px.scatter(df, y="start_weekday", x="start_hour", size="counts")

        return fig

        #st.plotly_chart(fig, use_container_width=True)


    def show_bookings_count(self):
        self.show_heading()
        count_col, agg_freq_= self.show_widgets()[0]
        fig = self.get_bookings_count(count_col, agg_freq_)
        st.plotly_chart(fig, use_container_width=True)

    def show_bookings_by_hour(self):
        self.show_heading()
        fig = self.get_bookings_by_hour()
        st.plotly_chart(fig, use_container_width=True)

    def show_bubble_plot(self):
        self.show_heading()
        fig = self.get_bubble_plot()
        st.plotly_chart(fig, use_container_width=True)