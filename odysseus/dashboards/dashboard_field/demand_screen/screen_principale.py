from odysseus.dashboards.dashboard_field.dashboard_screen import DashboardScreen
from odysseus.dashboards.dashboard_field.demand_screen.chart_map import ChartMap

from odysseus.dashboards.dashboard_field.utils import *

import pandas as pd
from functools import partial
import streamlit as st

import requests
from bson import json_util
import json
import numpy as np
from skmob.tessellation import tilers

class ScreenDemand(DashboardScreen):
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
        
        base_shapes = {"Torino": "Turin, Italy",
                        "Amsterdam":"Amsterdam, Netherlands"}
        tessellation = tilers.tiler.get("squared", base_shape = base_shapes[self.city_name], meters=500)
        tessellation.tile_ID = tessellation.tile_ID.astype(int)
        self.grid = tessellation

        with st.spinner('Fetching the '+ self.city_name +' time collections from DB'):
            self.temp_data = self.get_temp_collection()

        with st.spinner('Fetching the '+ self.city_name +' space collections from DB'):
            self.space_data = self.get_space_collection()
        _min = min(self.temp_data.date).to_pydatetime()
        _max = max(self.temp_data.date).to_pydatetime()
        
        param_list = list(self.temp_data.columns.difference(['city', 'date']))

        self.widget_list = [partial(st_functional_columns, [['date_input', "Inserisci la data di inizio analisi", _min, _min, _max], 
                                                            ['date_input', "Inserisci la data di fine analisi", _max, _min, _max]])]#,
                                                            #[ "selectbox", "Scegli il parametro", param_list]])]
        
    @st.cache(allow_output_mutation=True, show_spinner=False)
    def get_temp_collection(self):

        year_list =[]
        year_list.append(self.year)
        

        month_list =[]
        month_list.append(self.month)

        settings = {'id': 'TEST', 'city': self.city_name, 'year': str(year_list), 'month': str(month_list)}
        r = requests.get('http://127.0.0.1:5000/api_cdm/get-cdm-data', params=settings)
        json_df = pd.DataFrame(json.loads(r.text, object_hook=json_util.object_hook))
        
        ## Throw error se json_df è vuoto
        if (json_df.empty):
            st.error('dataframe vuoto')
            st.stop()

        #unlist the values
        df = json_df.set_index(['year', 'month', 'day', 'city']).apply(pd.Series.explode).reset_index()

        #add the hour column from unlisted values
        df['hour'] = pd.timedelta_range(0, periods=len(df.index), freq='H')
        df['hour'] = df.hour.apply(lambda x: round(x / np.timedelta64(1, 'h')) % 24 )

        #create date time column
        date_columns = ['year', 'month', 'day', 'hour']
        df['date'] = pd.to_datetime(df[date_columns])
        df = df.drop(date_columns, axis=1)

        return df


    @st.cache(allow_output_mutation=True, show_spinner=False)
    def get_space_collection(self):

        year_list =[]
        year_list.append(self.year)
        

        month_list =[]
        month_list.append(self.month)

        settings = {'id': 'TEST', 'city': self.city_name, 'year': str(year_list), 'month': str(month_list)}
        r = requests.get('http://127.0.0.1:5000/api_cdm/get-demand-data', params=settings)
        json_df = pd.DataFrame(json.loads(r.text, object_hook=json_util.object_hook))
        
        ## Throw error se json_df è vuoto
        if (json_df.empty):
            st.error('dataframe vuoto')
            st.stop()
        
        #unlist the values
        df = json_df.set_index(['year', 'month', 'day', 'city', 'data_source_id']).apply(pd.Series.explode).reset_index()
        
        date_columns = ['year', 'month', 'day']
        df['date'] = pd.to_datetime(df[date_columns])
        df = df.drop(date_columns, axis=1)
        
        df_plot = df.copy()
        df_plot[['out_flow_count','tile_ID']] = pd.DataFrame(df_plot.out_flow_count.tolist(), index= df_plot.index)
        df_plot[['in_flow_count','tile_ID']] = pd.DataFrame(df_plot.in_flow_count.tolist(), index= df_plot.index)
        df_plot[['origin_count','tile_ID']] = pd.DataFrame(df_plot.origin_count.tolist(), index= df_plot.index)
        
        
        #tessellation = tilers.tiler.get("squared", base_shape = base_shapes[self.city_name], meters=500)
        #tessellation.tile_ID = tessellation.tile_ID.astype(int)
        
        gdf = self.grid.merge(df_plot, on="tile_ID")
        return gdf
    



    def show_charts(self):

        start, end = self.show_widgets()[0]
        if start>=end:
            st.error('End limit date cannot be before the start date of analysis. Retry')
        else:
            #og_points = self.filter_map_data(self.data, start, end)

            #map_df = filtered_df.rename(columns={'start_latitude':'lat', 'start_longitude':'lng', 'start_time':'datetime'})
            #ChartMap(self.space_data, 'Heat Map', "This is a heatmap of the bookings during the month in exam. You can change the time interval also! The data analyst who thought about it is pretty smart, don't you think?", self.grid, start, end, tipo='heatmap', parametro=self.city_name).show_choropleth_mapbox()

            ChartMap(self.space_data, 'Heat Map', "This is a heatmap of the bookings during the month in exam. You can change the time interval also! The data analyst who thought about it is pretty smart, don't you think?", self.grid, start, end, tipo='heatmap', parametro=self.city_name).show_prova5()
