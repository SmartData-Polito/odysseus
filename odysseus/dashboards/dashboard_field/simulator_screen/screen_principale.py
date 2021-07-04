from odysseus.dashboards.dashboard_field.dashboard_screen import DashboardScreen
from odysseus.dashboards.dashboard_field.simulator_screen.chart_map import ChartMap
from odysseus.dashboards.dashboard_field.simulator_screen.chart_temp import ChartTemp



import streamlit as st
import os
import pandas as pd
import geopandas as gpd

class ScreenSimulator(DashboardScreen):
    def __init__(self, title, name, month, year, city, db="big_data_db", chart_list=None, subtitle=None, widget_list = None):
        super().__init__(title,name,chart_list,subtitle, widget_list)
        self.chart_dict = {}
        self.year = year
        self.month = month
        self.city_name = city
        self.data_source_id = db

        self.grid = None
        #self.result_path = self.get_simulaton_path()

        #st.write(self.result_path)


    def get_simulaton_path(self):

        sim_path = os.path.join(os.curdir, "odysseus", "simulator")
        dir = [f.name for f in os.scandir(sim_path) if (f.is_dir() and not f.name.endswith(".DS_Store"))]
        
        if "results" not in dir:
            st.error("No simulation as been run")
            st.stop()
        
        
        result_dir = os.path.join(os.curdir, "odysseus", "simulator", "results")
        city_dir = [f.name for f in os.scandir(result_dir) if (f.is_dir() and not f.name.endswith(".DS_Store"))]
        sim_city =  st.selectbox("Scegli quale città", city_dir)

        sim_type_path = os.path.join(os.curdir,  "odysseus", "simulator", "results", sim_city)
        sim_type_dir = [f.name for f in os.scandir(sim_type_path) if (f.is_dir() and not f.name.endswith(".DS_Store"))]
        sim_type =  st.selectbox("Scegli quale tipo di run", sim_type_dir)

        sim_name_path = os.path.join(os.curdir,  "odysseus", "simulator", "results", sim_city, sim_type)
        sim_name_dir = [f.name for f in os.scandir(sim_name_path) if (f.is_dir() and not f.name.endswith(".DS_Store"))]
        sim_scenario_name =  st.selectbox("Scegli run visualizzare", sim_name_dir)

        
        result_path = os.path.join(os.curdir,  "odysseus", "simulator", "results", sim_city, sim_type, sim_scenario_name)
        return result_path


    def show_charts(self):
        results_path = self.get_simulaton_path()

        self.stat_data = pd.read_csv(os.path.join(results_path, 'sim_stats.csv'))

        ChartTemp(self.stat_data, 'Event Plot', 'Percentage charts of the events simulated. \
            The first chart refers to how the trips have been satisfied: if the car was in the requested zone or in the near vicinity.\
            Second chart instead focuses on the unsatisfied trips and in what fashion this happened: if there where no cars available or \
            the energy in the chosen car was not sufficient to complete the trips. At last, the percentage of events that have been successful\
            versus the unsuccesful ones.  ').show_pie_chart()
        

        self.grid = gpd.read_file(os.path.join(results_path, "grid.shp"))

        ChartMap(self.grid, 'Zonal Analysis', 
        "In this map is shown different statistics by zone of the simulation you just run!", 
        parametro=self.city_name).show_choropleth_mapbox()

        sim_booking_requests = pd.read_csv(os.path.join(results_path, 'sim_booking_requests.csv'))
        ChartTemp(sim_booking_requests, 'Event Plot', 'Percentage charts of the events simulated. \
            The first chart refers to how the trips have been satisfied: if the car was in the requested zone or in the near vicinity.\
            Second chart instead focuses on the unsatisfied trips and in what fashion this happened: if there where no cars available or \
            the energy in the chosen car was not sufficient to complete the trips. At last, the percentage of events that have been successful\
            versus the unsuccesful ones.  ').show_cost()
        
