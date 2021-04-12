from odysseus.dashboards.dashboard_field.dashboard_field import DashboardField
import streamlit as st


class DashboardChart(DashboardField):

    def __init__(self, title, name, subtitle="", widget_list=None):
        super().__init__(title, location=st, widget_location=st, name=name, subtitle=subtitle, widget_list=widget_list)

    def show_heading(self):
        self.location.markdown("### **" + self.title+"**")
        self.location.markdown("*" +self.subtitle+"*")

    def show(self):
        """

        :return:
        """
