from odysseus.dashboards.dashboard_field.dashboard_chart import DashboardChart
from odysseus.dashboards.dashboard_field.utils import st_functional_columns

from odysseus.simulator.simulation_input.vehicle_conf import vehicle_conf


import streamlit as st
from functools import partial
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd



class ChartTemp(DashboardChart):

    def __init__(self, data, title, subtitle, tipo="Altair", parametro='plate'):
        super().__init__(title, name=title, subtitle=subtitle)
        self.data = data
        self.parametro=parametro
        self.tipo = tipo

        arg = [["selectbox", "Segli modello macchina", list(vehicle_conf['electric'].keys())],
            ['number_input', "Inserisci il costo dell'elettricità dell'infrastuttura per il distributore [€/kWh]", 0.0, 5.0, 0.1],
            ['number_input', "Inserisci il prezzo per l'utilizzo per l'utente [€/minuto]", 0.0, 1.0, 0.25]]

        self.widget_list= [partial(st_functional_columns, arg)]



    def get_pie_chart(self, title, values, label_name):

        layout = go.Layout(
            {
                "title":title
            }
        )

        data = {
            "values": values,
            "labels": label_name,
            "hoverinfo":"label+percent+name",
            "hole": .5,
            "type": "pie",
                "showlegend":False,
            }
        fig = go.Figure(data = data, layout = layout)

        return fig

    def show_pie_chart(self):
        self.show_heading()

        col1, col2, col3 = st.beta_columns(3)
        
        #col1
        df_fields = ["fraction_same_zone_trips_satisfied", "fraction_not_same_zone_trips_satisfied"]
        label_name = ["same zone", "neighbor zone"]
        title = "satisfied %"
        values = [
            self.data.loc[self.data['Unnamed: 0'] == df_fields[0], '0'].iloc[0],
            self.data.loc[self.data['Unnamed: 0'] == df_fields[1], '0'].iloc[0]]
        fig = self.get_pie_chart(title, values, label_name)
        col1.plotly_chart(fig, use_container_width=True)

        # col2
        df_fields = ["fraction_no_close_vehicles_unsatisfied", "fraction_deaths_unsatisfied"]
        label_name = ["no close vehicle", "not enough energy"]
        title = "unsatisfied %"
        values = [
            self.data.loc[self.data['Unnamed: 0'] == df_fields[0], '0'].iloc[0],
            self.data.loc[self.data['Unnamed: 0'] == df_fields[1], '0'].iloc[0]]
        fig = self.get_pie_chart(title, values, label_name)

        col2.plotly_chart(fig, use_container_width=True)

        # col3
        df_fields = ["fraction_unsatisfied", "fraction_satisfied"]
        label_name = ["unsatisfied", "satisfied"]
        title = "events %"
        values = [
            self.data.loc[self.data['Unnamed: 0'] == df_fields[0], '0'].iloc[0],
            self.data.loc[self.data['Unnamed: 0'] == df_fields[1], '0'].iloc[0]]
        fig = self.get_pie_chart(title, values, label_name)

        col3.plotly_chart(fig, use_container_width=True)



    def get_cost(self, car_model, car_cost, fuel_cost):

        engine_type = 'electric'
        consumption = vehicle_conf[engine_type][car_model]["consumption"] #km/l, km/kWh
	
        test_df = self.data.copy()

        test_df['fuel_cost'] = test_df.apply(lambda x: self.distance_to_cost(x['driving_distance'], consumption, fuel_cost), axis=1)

        test_df.start_time = pd.to_datetime(test_df.start_time)
        test_df.end_time = pd.to_datetime(test_df.end_time)

        test_df['user_gain'] = test_df.apply(lambda x: self.time_to_cost(x['start_time'], x['end_time'], car_cost), axis=1)

        plot_df = test_df.set_index('start_time').resample(
            "60Min"
        ).sum().asfreq("60Min", fill_value=0)
        # cost to be added
        fig = px.line(plot_df, y=['fuel_cost', 'user_gain'])
        fig.update_layout(
            xaxis_title="Time series",
            yaxis_title="Cost [€]",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="MediumSlateBlue"
            )
        )

        return fig


    def show_cost(self):
        self.show_heading()
        car_model, fuel_cost , car_cost = self.show_widgets()[0]
        fig = self.get_cost(car_model, car_cost, fuel_cost)
        st.plotly_chart(fig, use_container_width=True)


    def from_kml_to_lkm(self, consumption):
        return 1 / consumption

    def distance_to_cost(self, distance, consumption, fuel_cost):
        perkm_consumption = self.from_kml_to_lkm(consumption)
        tot_consumption = perkm_consumption * distance * fuel_cost / 1000
        return tot_consumption


    def time_to_cost(self, start, end, cost):
        use_in_minutes = int((end-start).total_seconds()/60)
        tot_cost = use_in_minutes*cost
        return tot_cost
