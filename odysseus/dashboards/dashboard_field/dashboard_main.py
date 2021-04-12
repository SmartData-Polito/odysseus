import streamlit as st

from odysseus.dashboards.dashboard_field.dashboard_field import DashboardField
from odysseus.dashboards.dashboard_field.citydatamanager_screen.screen_principale import ScreenPrincipale

from odysseus.city_data_manager.config.config import cities # get all possible city names from config files
from functools import partial

class DashboardMain(DashboardField):


    """
        city_name = st.sidebar.selectbox(
        'City:',
        cities
    )

    
    selected_month = st.sidebar.selectbox('Month', [10]) 
    selected_year = st.sidebar.selectbox('Year', [2017])

    selected_source = st.sidebar.selectbox('Source', ["big_data_db"])
    """

    def __init__(self, title, available_fields, subtitle = "", logo=""):
        self.available_screens_list = available_fields
        wl = [partial(st.sidebar.selectbox, "Scegli quale schermata visualizzare", ["City Data Manager"]),
            partial(st.sidebar.selectbox, "Scegli quale città", cities),
            partial(st.sidebar.selectbox, "Scegli quale mese", [10]),
            partial(st.sidebar.selectbox, "Scegli quale anno", [2017]),
            partial(st.sidebar.selectbox, "Scegli quale data source", ["big_data_db"])]
        super().__init__(widget_location=st.sidebar, title=title, name="Schermata principale", subtitle=subtitle, widget_list=wl)
        self.logo = logo


    def show_heading(self):
        self.widget_location.image(self.logo)
        self.location.markdown("# "+self.title)


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
        
    def show(self):
        self.show_heading()

        name, city, month, year, db = self.show_widgets()
        main_screen= ScreenPrincipale(title="Titolo: " + name, name=name,month = month, year = year, city = city)
        main_screen.show_heading()
        main_screen.show_charts()