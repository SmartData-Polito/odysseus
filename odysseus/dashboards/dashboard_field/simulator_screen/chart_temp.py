from odysseus.dashboards.dashboard_field.dashboard_chart import DashboardChart
from odysseus.dashboards.dashboard_field.utils import st_functional_columns

import streamlit as st
from functools import partial
import plotly.express as px
import plotly.graph_objs as go



class ChartTemp(DashboardChart):

    def __init__(self, data, title, subtitle, tipo="Altair", parametro='plate'):
        super().__init__(title, name=title, subtitle=subtitle)
        self.data = data
        self.parametro=parametro
        self.tipo = tipo


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
