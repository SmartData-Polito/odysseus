import streamlit as st
import os

from odysseus.dashboards.dashboard_field.dashboard_field import DashboardField
from odysseus.dashboards.dashboard_field.home_screen import ScreenHome
from odysseus.dashboards.dashboard_field.citydatamanager_screen.screen_principale import ScreenDataManager
from odysseus.dashboards.dashboard_field.demand_screen.screen_principale import ScreenDemand
from odysseus.dashboards.dashboard_field.supply_screen.screen_principale import ScreenSupply
from odysseus.dashboards.dashboard_field.simulator_screen.screen_principale import ScreenSimulator

from odysseus.city_data_manager.config.config import cities # get all possible city names from config files
from functools import partial
import pymongo

class DashboardMain(DashboardField):


    def __init__(self, title, available_fields, subtitle = "", logo=""):
        self.available_screens_list = available_fields
        super().__init__(widget_location=st.sidebar, title=title, name="Schermata principale", subtitle=subtitle, widget_list=None)
        self.logo = logo

    def show_heading(self):
        self.widget_location.image(self.logo)
        self.location.markdown("# "+self.title)

    def show_widgets(self):
        
        name = st.sidebar.selectbox("Scegli quale schermata visualizzare", ["Home Page", "City Data Manager", "Demand Modelling", "Supply Modelling", "Simulator"])

        city_path = os.path.join(os.curdir, "odysseus", "city_data_manager", "data")
        city_dir = os.listdir( city_path )
        city =  st.sidebar.selectbox("Scegli quale città", city_dir)

        db_path = os.path.join(os.curdir, "odysseus", "city_data_manager", "data", city, "od_trips", "points")
        db_dir = os.listdir( db_path )
        db = st.sidebar.selectbox("Scegli quale città", db_dir)

        ym_path = os.path.join(os.curdir, "odysseus", "city_data_manager", "data", city, "od_trips", "points", db)
        ym_dir = os.listdir( ym_path )
        
        splitList=set([item.split(".")[0] for item in ym_dir])

        years = set([item.split("_")[0] for item in splitList])
        year = st.sidebar.selectbox("Scegli l'anno", list(years))

        months = set([item.split(year+"_")[1] for item in splitList])
        month = st.sidebar.selectbox("Scegli l'mese", list(months))
        
        ret = [name, city, month, year, db]
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

    def get_main_screen(self, name, month, year, city, db):
        if name == "Home Page":
            main_screen = ScreenHome(title="Titolo: " + name, name=name,month = month, year = year, city = city, db = db)
        elif name == "City Data Manager":
            main_screen = ScreenDataManager(title="Titolo: " + name, name=name,month = month, year = year, city = city, db = db)
        elif name == "Demand Modelling":
            main_screen= ScreenDemand(title="Titolo: " + name, name=name,month = month, year = year, city = city)
        elif name == "Supply Modelling":
            main_screen= ScreenDemand(title="Titolo: " + name, name=name,month = month, year = year, city = city)
        elif name == "Simulator":
            main_screen= ScreenDemand(title="Titolo: " + name, name=name,month = month, year = year, city = city)
 #       
        return main_screen

    def show(self):
        self.show_heading()

        name, city, month, year, db = self.show_widgets()
        client = pymongo.MongoClient("localhost", 27017)
        mongo_db = client["city_data_manager"]
        main_screen= self.get_main_screen(name, month, year, city, db)
        main_screen.show_heading()
        main_screen.show_charts()