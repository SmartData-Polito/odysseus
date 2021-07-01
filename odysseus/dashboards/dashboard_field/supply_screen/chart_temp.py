from odysseus.dashboards.dashboard_field.dashboard_chart import DashboardChart
from odysseus.dashboards.dashboard_field.utils import st_functional_columns
from odysseus.simulator.simulation_input.vehicle_conf import vehicle_conf

from odysseus.dashboards import session_state as SessionState
from threading import Thread
import streamlit as st
from functools import partial
import pandas as pd
import datetime

import plotly.express as px


class ChartTemp(DashboardChart):

    def __init__(self, data, year, month, start, end, stat_col, title, subtitle, tipo="Altair", parametro='plate'):
        super().__init__(title, name=title, subtitle=subtitle)
        self.data = data
        self.parametro=parametro
        self.tipo = tipo
        self.year= year
        self.month = month
        self.startDay = start
        self.endDay = end
        self.car_type = stat_col
        arg = [["selectbox", "Scegli aggregazione", ["1H", "3H", "6H", "12H","1D", "2D", "3D"]],
                ["selectbox", "Segli modello macchina", list(vehicle_conf[self.car_type].keys())],
                ['number_input', "Inserisci il prezzo del carburante", 0, 10, 1]]
        
        self.widget_list= [partial(st_functional_columns, arg)]

    def get_bookings_count(self, agg_freq_, car_model, price):

        engine_type = vehicle_conf[self.car_type][car_model]["engine_type"] #gasoline, diesel, lpg, gnc, electric
        consumption = vehicle_conf[self.car_type][car_model]["consumption"] #km/l, km/kWh
        capacity = vehicle_conf[self.car_type][car_model]["fuel_capacity"] #kWh (electric), Liter (gasoline,diesel,lpg), kilograms (gnc)
		
        st.write("Engine type is:")
        st.write(engine_type)

        st.write("Consumpion is:")
        st.write(consumption)

        st.write("from_kml_to_lkm: ")
        st.write(self.from_kml_to_lkm(consumption))
        column = 'sum_euclidean_distance'

        test_df = self.data.copy()
        test_df = test_df.assign(consumption = lambda x:(self.distance_to_cost(x[column], consumption, price)))
        
        plot_df = test_df.set_index('date').resample(
            agg_freq_
        ).sum().asfreq(agg_freq_, fill_value=0)
        # cost to be added
        plot_df = plot_df['consumption'].loc[self.startDay:self.endDay]
        fig = px.line(plot_df)
        fig.update_layout(
            xaxis_title="Time series",
            yaxis_title="Tot. consumption",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="MediumSlateBlue"
            )
        )

        return fig

    def show_bookings_count(self):
        self.show_heading()
        agg_freq_,car_model, price = self.show_widgets()[0]
        fig = self.get_bookings_count(agg_freq_, car_model, price)
        st.plotly_chart(fig, use_container_width=True)


    def from_kml_to_lkm(self, consumption):
        return 1 / consumption

    def distance_to_cost(self, distance, consumption, price):
        perkm_consumption = self.from_kml_to_lkm(consumption)
        tot_consumption = perkm_consumption * distance * price
        return tot_consumption
