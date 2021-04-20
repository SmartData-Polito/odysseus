import os
import plotly.express as px
from odysseus.dashboards.dashboard_field.dashboard_screen import DashboardScreen
from odysseus.dashboards.dashboard_field.citydatamanager_screen.chart_temp import ChartTemp
from odysseus.dashboards.dashboard_field.citydatamanager_screen.chart_map import ChartMap

from odysseus.city_data_manager.config.config import *
import pandas as pd

import pytz
import geopandas as gpd
import shapely
import datetime
from functools import partial
import streamlit as st
from streamlit.report_thread import add_report_ctx


class ScreenDataManager(DashboardScreen):
    def __init__(self, title, name, month, year, city, db="big_data_db", chart_list=None, subtitle=None, widget_list = None):
        super().__init__(title,name,chart_list,subtitle, widget_list)
        self.chart_dict = {}
        self.year = year
        self.month = month
        self.city_name = city
        self.data_source_id = db

        self.trips = None
        self.trips_destinations = None
        self.trips_origins = None

        self.points_data_path = os.path.join(
            data_paths_dict[self.city_name]["od_trips"]["points"],
            self.data_source_id,
            "_".join([str(year), str(month)])
        )

        self.trips_data_path = os.path.join(
            data_paths_dict[self.city_name]["od_trips"]["trips"],
            self.data_source_id,
            "_".join([str(year), str(month)])
        )

        if self.city_name == "Roma" or self.city_name == "Torino" or self.city_name == "Milano":
            self.tz = pytz.timezone("Europe/Rome")
        elif self.city_name == "Amsterdam":
            self.tz = pytz.timezone("Europe/Amsterdam")
        elif self.city_name == "Madrid":
            self.tz = pytz.timezone("Europe/Madrid")
        elif self.city_name == "Berlin":
            self.tz = pytz.timezone("Europe/Berlin")
        elif self.city_name == "New_York_City":
            self.tz = pytz.timezone("America/New_York")
        elif self.city_name == "Vancouver":
            self.tz = pytz.timezone("America/Vancouver")
        elif self.city_name == "Louisville":
            self.tz = pytz.timezone("America/Kentucky/Louisville")
        elif self.city_name == "Minneapolis" or self.city_name == "Chicago":
            self.tz = pytz.timezone("America/Chicago")
        elif self.city_name == "Austin" or self.city_name == "Kansas City":
            self.tz = pytz.timezone("US/Central")
        elif self.city_name == "Norfolk":
            self.tz = pytz.timezone("US/Eastern")
        elif self.city_name == "Calgary":
            self.tz = pytz.timezone("Canada/Mountain")

        self.data = self.read_origin_data()

        
        min = datetime.datetime.fromisoformat(str(self.data['start_time'].min()))
        max = datetime.datetime.fromisoformat(str(self.data['start_time'].max()))

        #args = [["slider", "Va che bello questo slider", min, max, (min, max)]]

        self.widget_list = [partial(st.slider, "slider test", min, max, (min, max))]

    @st.cache(allow_output_mutation=True)
    def read_origin_data (self):

        path = os.path.join(
            self.trips_data_path,
            "trips.csv"
        )
        df_trips = pd.read_csv(path)
        df_trips['geometry'] = df_trips['geometry'].apply(shapely.wkt.loads)
        self.trips = gpd.GeoDataFrame(df_trips, geometry='geometry')

        path_og = os.path.join(
            self.points_data_path,
            "origins.csv"
        )
        df_og = pd.read_csv(path_og)
        df_og['geometry'] = df_og['geometry'].apply(shapely.wkt.loads)
        self.trips_origins = gpd.GeoDataFrame(df_og, geometry='geometry')

        path_dt = os.path.join(
            self.points_data_path,
            "destinations.csv"
        )
        df_dt = pd.read_csv(path_dt)
        df_dt['geometry'] = df_dt['geometry'].apply(shapely.wkt.loads)
        self.trips_destinations = gpd.GeoDataFrame(df_dt, geometry='geometry')

        self.trips_origins.crs = "epsg:4326"
        self.trips_destinations.crs = "epsg:4326"
        self.trips_origins["start_longitude"] = self.trips_origins.geometry.apply(lambda p: p.x)
        self.trips_origins["start_latitude"] = self.trips_origins.geometry.apply(lambda p: p.y)
        self.trips_destinations["end_longitude"] = self.trips_destinations.geometry.apply(lambda p: p.x)
        self.trips_destinations["end_latitude"] = self.trips_destinations.geometry.apply(lambda p: p.y)

        if self.city_name == 'Vancouver':
            self.trips = self.trips[self.trips.start_longitude < -122.9]
            self.trips = self.trips[self.trips.end_longitude < 0]
        elif self.city_name == 'Berlin':
            self.trips = self.trips[(self.trips.start_latitude > 51) & (self.trips.start_latitude < 53)]
            self.trips = self.trips[(self.trips.start_longitude > 12) & (self.trips.start_longitude < 14)]
            self.trips = self.trips[(self.trips.end_latitude > 51) & (self.trips.end_latitude < 53)]
            self.trips = self.trips[(self.trips.end_longitude > 12) & (self.trips.end_longitude < 14)]
        elif self.city_name == 'Kansas City':
            self.trips = self.trips[(self.trips.start_latitude > 38.95) & (self.trips.start_latitude < 39.20)]
            self.trips = self.trips[(self.trips.end_latitude > 38.95) & (self.trips.end_latitude < 39.20)]

        self.trips_origins = self.trips_origins.loc[self.trips.index]
        self.trips_destinations = self.trips_destinations.loc[self.trips.index]

        self.trips.start_time = pd.to_datetime(self.trips.start_time)
        self.trips_origins.start_time = self.trips.start_time
        self.trips.end_time = pd.to_datetime(self.trips.end_time)
        self.trips_destinations.end_time = self.trips.end_time

        return self.trips_origins
        
    def show_charts(self):

        start, end = self.show_widgets()[0]
        filtered_df = self.filter_data(self.data, start, end)
        #self.filter_data(self.data, start, end)

        map_df = filtered_df.rename(columns={'start_latitude':'lat', 'start_longitude':'lng', 'start_time':'datetime'})
        ChartTemp(filtered_df, 'Bookings Count', 'Here is a time series showing how many cars within our fleet are booked at any given time. You can see how it behaves based on different frequencies and zoom in during specific periods in the month! Have fun!').show_bookings_count()

        ChartTemp(filtered_df, 'Hourly Bookings', "here is a bar plot showing the distribution of the usage of cars in our fleet based on the hour in which were booked during the specified month. Isn't it cool?").show_bookings_by_hour()

        ChartTemp(filtered_df, 'Bubble Plot', 'What a peculiar graph we have here! this is a bubble plot here each bubble is bigger the more bookings we had during a specific hour and a specific day of the week. Can you spot the biggest one?').show_bubble_plot()
        
        thread1 = ChartMap(map_df, 'Heat Map', "This is a heatmap of the bookings during the month in exam. You can change the time interval also! The data analyst who thought about it is pretty smart, don't you think?", tipo='heatmap', parametro=self.city_name)
        add_report_ctx(thread1)
        thread1.start()
        
        thread2 = ChartMap(map_df, 'Andamento Spazio-temporale', 'Ho finito le battute, tieni il grafico, vedi tu. premi play, premi il play al contrario boh',tipo='heatmapWithTime', parametro=self.city_name)
        add_report_ctx(thread2)
        thread2.start()

        thread1.join()
        thread2.join()

    @st.cache(allow_output_mutation=True)
    def filter_data(self, df, start, end):
        df['start_time'] = pd.to_datetime(df['start_time'], utc=True)
        filtered_df = df.loc[(df['start_time'] >= start)
                        & (df['start_time'] < end)]
        
        return filtered_df