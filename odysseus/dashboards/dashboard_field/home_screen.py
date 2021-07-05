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

        st.success("Greetings Traveller")

        st.markdown('**ODySSEUS** is a data management and simulation software for mobility data, focused mostly on shared fleets in urban environments.')

        st.markdown('Its goal is to provide a general, easy-to-use framework to _simulate shared mobility scenarios_ across different cities using **real-world data**.')

        st.markdown('What you are looking at right now is a *dashboard* where you can analize and see the data that you have at your disposal and the results of the simulations have run')

        st.markdown('At your left you can see a **sidebar** where you can navigate the dashboard and the gathered data. Here you can choose:')

        st.markdown('1. The section of the software you want to look at (i.e. City Data manager, Demand Modelling, Supply Modelling and SImulator)')
        st.markdown('2. The city of interest')
        st.markdown('3. The source of the data anlized')
        st.markdown('4. the year of interest')
        st.markdown('5. and finally the month of interest')

        st.markdown('At the end of the sidebard there is a handy button that brings you back to the web application with all the forms if in need of rerunning the modules one again')


        
