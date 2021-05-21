from odysseus.dashboards.dashboard_field.dashboard_chart import DashboardChart
from odysseus.dashboards.dashboard_field.utils import st_functional_columns

import streamlit as st
from functools import partial
import pandas as pd
import datetime

import plotly.express as px
import pymongo


class ChartTemp(DashboardChart):

    def __init__(self, data, year, month, start, end, title, subtitle, tipo="Altair", parametro='plate'):
        super().__init__(title, name=title, subtitle=subtitle)
        self.temp_data = data
        self.parametro=parametro
        self.tipo = tipo
        self.year= year
        self.month = month
        self.startDay = start
        self.endDay = end
        arg = [[    "selectbox", "Scegli il parametro", ['avg_duration', 'n_booking']], 
                ["selectbox", "Scegli aggregazione", ["1H", "3H", "6H", "12H","1D", "2D", "3D"]]]

        self.widget_list= [partial(st_functional_columns, arg)]

    def get_bookings_count(self, column, agg_freq_):

        plot_df = self.temp_data.set_index('date').resample(
            agg_freq_
        ).sum().asfreq(agg_freq_, fill_value=0)

        plot_df = plot_df[column].loc[self.startDay:self.endDay]
        fig = px.line(plot_df)
        fig.update_layout(
            xaxis_title="Time series",
            yaxis_title="Number of Trips",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="MediumSlateBlue"
            )
        )

        return fig

    def get_bookings_by_hour(self):

        bar_plot = self.temp_data.groupby(self.temp_data.date.dt.hour).n_booking.sum()
        fig = px.bar(bar_plot)
        fig.update_layout(
            xaxis_title="Hour of the day",
            yaxis_title="Number of trips",
            legend_title="Legend Title",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="MediumSlateBlue"
            )
        )
        return fig


    def get_bubble_plot(self):

        bubble_plot = self.temp_data
        bubble_plot['dayOfWeek'] = self.temp_data.date.dt.dayofweek
        days = {0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri', 5:'Sat',6:'Sun'}
        bubble_plot['dayOfWeek'] = bubble_plot['dayOfWeek'].apply(lambda x: days[x])
        bubble_plot['hour'] = self.temp_data.date.dt.hour
        fig = px.scatter(bubble_plot, y="dayOfWeek", x="hour", size="n_booking")
        fig.update_layout(
            xaxis_title="Hour of the day",
            yaxis_title="Day Of the Week",
            legend_title="Legend Title",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="MediumSlateBlue"
            )
        )
        return fig


    def show_bookings_count(self):
        self.show_heading()
        count_col, agg_freq_= self.show_widgets()[0]
        fig = self.get_bookings_count(count_col, agg_freq_)
        st.plotly_chart(fig, use_container_width=True)

    def show_bookings_by_hour(self):
        self.show_heading()
        #count_col, _= self.show_widgets()[0]
        fig = self.get_bookings_by_hour()
        st.plotly_chart(fig, use_container_width=True)

    def show_bubble_plot(self):
        self.show_heading()
        #count_col, _= self.show_widgets()[0]
        fig = self.get_bubble_plot()
        st.plotly_chart(fig, use_container_width=True)
