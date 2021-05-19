import os
import plotly.express as px
from odysseus.dashboards.dashboard_field.dashboard_screen import DashboardScreen
from odysseus.dashboards.dashboard_field.citydatamanager_screen.chart_temp import ChartTemp
from odysseus.dashboards.dashboard_field.citydatamanager_screen.chart_map import ChartMap

from odysseus.dashboards.dashboard_field.utils import *

from odysseus.city_data_manager.config.config import *
import pandas as pd

import pytz
import geopandas as gpd
import shapely
import datetime
from functools import partial
import streamlit as st
from streamlit.report_thread import add_report_ctx
import pymongo as pm

import requests
from bson import json_util
import json


class ScreenDataManager(DashboardScreen):
    def __init__(self, title, name, month, year, city, db="big_data_db", chart_list=None, subtitle=None, widget_list = None):
        super().__init__(title,name,chart_list,subtitle, widget_list)
        self.chart_dict = {}
        self.year = int(year)
        self.month = int(month)
        self.city_name = city
        self.data_source_id = db

        self.trips = None
        self.trips_destinations = None
        self.trips_origins = None
        with st.spinner('Fetching the '+ self.city_name +' collections from DB'):
            self.temp_data = self.get_temp_collection()
            
        _min = min(self.temp_data.date).to_pydatetime()
        _max = max(self.temp_data.date).to_pydatetime()
        print(type(_min))
        #_list = self.temp_data.find({}, {'year':1, 'month': 1, 'day':1, '_id':0})
        #date_list = [datetime.datetime(x['year'], x['month'], x['day']) for x in _list]
        #_min = min(date_list)
        #_max= max(date_list)

        self.widget_list = [partial(st_functional_columns, [['date_input', "Inserisci la data di inizio analisi", _min, _min, _max], ['date_input', "Inserisci la data di fine analisi", _max, _min, _max]]) ]
    
    @st.cache(allow_output_mutation=True, show_spinner=False)
    def get_temp_collection(self):

        year_list =[]
        year_list.append(self.year)
        

        month_list =[]
        month_list.append(self.month)

        settings = {'id': 'TEST', 'city': self.city_name, 'year': str(year_list), 'month': str(month_list)}
        r = requests.get('http://127.0.0.1:5000/api_cdm/get-cdm-data', params=settings)
        json_df = pd.DataFrame(json.loads(r.text, object_hook=json_util.object_hook))
        json_df['date'] = pd.to_datetime(json_df['date'],utc=True).dt.to_pydatetime()
        return json_df

    def show_charts(self):

        start, end = self.show_widgets()[0]
        if start>=end:
            st.error('End limit date cannot be before the start date of analysis. Retry')
        else:
            #og_points = self.filter_map_data(self.data, start, end)

            #map_df = filtered_df.rename(columns={'start_latitude':'lat', 'start_longitude':'lng', 'start_time':'datetime'})
            
            ChartTemp(self.temp_data, self.year, self.month, start, end, 'Bookings Count', 'Here is a time series showing how many cars within our fleet are booked at any given time. You can see how it behaves based on different frequencies and zoom in during specific periods in the month!').show_bookings_count()

            ChartTemp(self.temp_data, self.year, self.month, start, end,'Hourly Bookings', "here is a bar plot showing the distribution of the usage of cars in our fleet based on the hour in which were booked during the specified month.").show_bookings_by_hour()

            ChartTemp(self.temp_data, self.year, self.month, start, end,'Bubble Plot', 'This is a bubble plot. here each bubble is bigger the more bookings we had during a specific hour and a specific day of the week.').show_bubble_plot()
            
            """ thread1 = ChartMap(og_points, 'Heat Map', "This is a heatmap of the bookings during the month in exam. You can change the time interval also! The data analyst who thought about it is pretty smart, don't you think?", tipo='heatmap', parametro=self.city_name)
            add_report_ctx(thread1)
            thread1.start()
            
            thread2 = ChartMap(og_points, 'Andamento Spazio-temporale', 'Ho finito le battute, tieni il grafico, vedi tu. premi play, premi il play al contrario boh',tipo='heatmapWithTime', parametro=self.city_name)
            add_report_ctx(thread2)
            thread2.start()

            thread1.join()
            thread2.join() """

    def filter_map_data(self, df, start, end):

        coll = self.data
        year = self.year
        month = self.month
        
        pipeline = [ 
            {  
                '$match' : { 'day': {'$gte': start.day, '$lte': end.day}}
            },
            {  
                '$project':{ 
                    '_id':0, 
                    'start_points':1,
                    'end_points':1,
                    'datetime': {'$dateFromParts': {'year':year, 
                                                    'month': month,
                                                'day': '$day',
                                                'hour':"$hour"}
                                }
                }
            }
        ]
        res = pd.DataFrame(list(coll.aggregate(pipeline)))
        df_exploded = res.set_index('datetime').apply(pd.Series.explode).reset_index()
        df_exploded[['start_lat','start_long']] = pd.DataFrame(df_exploded.start_points.tolist(), index= df_exploded.index)
        #df_exploded[['end_lat','end_long']] = pd.DataFrame(df_exploded.end_points.tolist(), index= df_exploded.index)

        start_df = df_exploded[['datetime', 'start_lat','start_long']]
        #end_df = df_exploded[['datetime', 'end_lat','end_long']]
        start_df = start_df.rename(columns={'start_lat':'lat', 'start_long':'lng'})
        return start_df#, end_df