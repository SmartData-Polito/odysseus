from odysseus.dashboards.dashboard_field.dashboard_screen import DashboardScreen
import streamlit as st

class ScreenHome(DashboardScreen):
    def __init__(self, title, name, month, year, city, db="big_data_db", chart_list=None, subtitle=None, widget_list = None):
        super().__init__(title,name,chart_list,subtitle, widget_list)
        self.chart_dict = {}
        self.year = year
        self.month = month
        self.city_name = city
        self.data_source_id = db


    def show_charts(self):
        st.success("Salve Prof Mellia")
