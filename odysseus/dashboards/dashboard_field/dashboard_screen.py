from odysseus.dashboards.dashboard_field.dashboard_field import DashboardField
import streamlit as st

class DashboardScreen(DashboardField):

    def __init__(self, title, name, chart_list=None, subtitle="", widget_list=None):
        super().__init__(title=title, widget_location=st, name=name, subtitle=subtitle, widget_list=widget_list)
        if chart_list is None:
            chart_list = []
        self.chart_list = chart_list

    def show_heading(self):
        self.location.markdown("## "+self.title)
        if self.subtitle is not None:
            self.location.write(self.subtitle)

    @st.cache(allow_output_mutation=True)
    def show_charts(self):
        for chart in self.chart_list:
            chart.show()



