import streamlit as st
import os

from odysseus.dashboards.dashboard_field.dashboard_field import DashboardField
from odysseus.dashboards.dashboard_field.home_screen import ScreenHome
from odysseus.dashboards.dashboard_field.citydatamanager_screen.screen_principale import ScreenDataManager
from odysseus.dashboards.dashboard_field.demand_screen.screen_principale import ScreenDemand
from odysseus.dashboards.dashboard_field.supply_screen.screen_principale import ScreenSupply
from odysseus.dashboards.dashboard_field.simulator_screen.screen_principale import ScreenSimulator

from odysseus.dashboards.dashboard_field.utils import *


from odysseus.city_data_manager.config.config import cities # get all possible city names from config files
from functools import partial

import requests
import json

import webbrowser

class DashboardMain(DashboardField):


    def __init__(self, title, available_fields, subtitle = "", logo=""):
        self.available_screens_list = available_fields
        super().__init__(widget_location=st.sidebar, title=title, name="Schermata principale", subtitle=subtitle, widget_list=None)
        self.logo = logo
        r = requests.get('http://127.0.0.1:5000/api_cdm/available-data-on-db')

        self.available_data = r.json()

    def show_heading(self):
        self.widget_location.image(self.logo)
        self.location.markdown("# "+self.title)

    def show_widgets(self):
        
        name = st.sidebar.selectbox("Scegli quale schermata visualizzare", ["Home Page", "City Data Manager", "Demand Modelling", "Supply Modelling", "Simulator"])
        
        

        available_cities = list(self.available_data.keys())
        city =  st.sidebar.selectbox("Scegli quale città", available_cities)

        available_dbs = list(self.available_data[city].keys())
        db = st.sidebar.selectbox("Scegli la data source", available_dbs)

        available_years = list(self.available_data[city][db].keys())

        year = st.sidebar.selectbox("Scegli l'anno", list(available_years))
        
        available_months = self.available_data[city][db][year]
        month = st.sidebar.selectbox("Scegli il mese", sorted(available_months))
        
        st.sidebar.markdown("The next widgest are needed to gather the simulation output data. Of course, if no simulation has been run, you can brows the city data manager or go to the react pahe and run it!")

        results_path = get_simulaton_path()

        ret = [name, city, month, year, db, results_path]
        col1, col2, col3 = st.sidebar.beta_columns([1,1,1])
        if col2.button('Go to React'):
            webbrowser.open_new_tab('127.0.0.1:3000')

        return tuple(ret)


    def get_screen_names(self):
        list = self.available_screens_list
        ret = []
        if len(list)==0:
            return ret
        for screen in list:
            ret.append(screen.get_name())
        return ret

    def show_screen(self, screen_name):
        for screen in self.available_screens_list:
            if screen.get_name() == screen_name:
                screen.show_heading()
                screen.show_charts()
                break

    def get_main_screen(self, name, month, year, city, db, res_path):
        
        if name == "Home Page":
            main_screen = ScreenHome(title="Titolo: " + name, name=name,month = month, year = year, city = city, db = db)
        elif name == "City Data Manager":
            main_screen = ScreenDataManager(title="Titolo: " + name, name=name,month = month, year = year, city = city, db = db)
        elif name == "Demand Modelling":
            main_screen= ScreenDemand(title="Titolo: " + name, name=name,month = month, year = year, city = city, result_path=res_path)
        elif name == "Supply Modelling":
            main_screen= ScreenSupply(title="Titolo: " + name, name=name,month = month, year = year, city = city)
        elif name == "Simulator":
            main_screen= ScreenSimulator(title="Titolo: " + name, name=name,month = month, year = year, city = city, result_path=res_path)
 #       
        return main_screen

    def show(self):
        self.show_heading()

        name, city, month, year, db, path = self.show_widgets()
        main_screen= self.get_main_screen(name, month, year, city, db, path)
        main_screen.show_heading()
        main_screen.show_charts()
