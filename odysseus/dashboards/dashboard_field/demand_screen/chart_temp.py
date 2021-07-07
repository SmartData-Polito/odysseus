from odysseus.dashboards.dashboard_field.dashboard_chart import DashboardChart
from odysseus.dashboards.dashboard_field.utils import st_functional_columns
import plotly.graph_objects as go


import streamlit as st
from functools import partial
import pandas as pd
import datetime

import plotly.express as px

class ChartTemp(DashboardChart):

    def __init__(self, data_model, data_trace, title, subtitle, tipo="Altair", parametro='plate'):
        super().__init__(title, name=title, subtitle=subtitle)
        self.data_model = self.to_plot_df(data_model)
        self.data_trace = self.to_plot_df(data_trace)
        self.parametro=parametro
        self.tipo = tipo
        arg = [["selectbox", "Scegli statistica", ['driving_distance', 'duration']]]

        self.widget_list= [partial(st_functional_columns, arg)]


    def get_statistics(self, data_to_show):
        column = data_to_show[0]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.data_model.index, y=self.data_model[column],
                            name='Model',
                                line=dict(color='royalblue')))
        #fig.add_trace(go.Scatter(x=self.data_trace.index, y=self.data_trace[column],
        #                    name='Trace',
        #                        line=dict(color='firebrick')))

        title_str = column.replace('_', ' ').title()
        fig.update_layout(
                        yaxis_title=title_str,
                        xaxis_title='Time series',
                            font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color="MediumSlateBlue"
                    ))

        return fig

    def to_plot_df(self, test_df):
        test_df.start_time = pd.to_datetime(test_df.start_time)
        plot_df = test_df.set_index('start_time').resample(
                    "60Min"
                ).sum().asfreq("60Min", fill_value=0)
        result = plot_df.copy()
        drop_list = list(result.columns.difference(['driving_distance', 'duration']))
        result = result.drop(drop_list, axis=1)
        return result


    def show_statistics(self):
        self.show_heading()
        stat_col = self.show_widgets()[0]
        fig = self.get_statistics(stat_col)
        st.plotly_chart(fig, use_container_width=True)

