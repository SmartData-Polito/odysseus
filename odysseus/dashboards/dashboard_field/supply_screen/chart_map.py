from odysseus.dashboards.dashboard_field.dashboard_chart import DashboardChart
from odysseus.dashboards.dashboard_field.utils import st_functional_columns

from odysseus.dashboards.dashboard_field.utils import *


import streamlit as st
from functools import partial

import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import shapely
from streamlit_plotly_events import plotly_events

import ast
class ChartMap(DashboardChart):

    def __init__(self, og_data, grid, title, subtitle, tipo="heatmap", parametro='Torino'):
        
        DashboardChart.__init__(self, title, name=title, subtitle=subtitle)
        self.og_data = og_data
        #self.dest_data = dest_data
        self.parametro=parametro
        self.tipo = tipo
        self.grid = grid
        arg = [["selectbox", "Scegli grafico", ['out_flow_count', 'in_flow_count','origin_count']]]

        self.widget_list= [partial(st_functional_columns, arg)]

    def getmap(self, gdf):
        bottom = st.empty()
        fig = px.choropleth_mapbox(gdf,
                                geojson=gdf.geometry,
                                locations=gdf.tile_ID,
                                #color="zone_id",
                                opacity=0.5,
                                center=city_centroid[self.parametro],
                                mapbox_style="open-street-map",
                                zoom=10)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.update(layout_coloraxis_showscale=False)

        with bottom:
            a = plotly_events(fig, hover_event=False, override_width=1000, select_event=False)

        return a

    def show_amenities_map(self):

        self.show_heading()

        form = st.form("Infrasrtrutture di interesse")
        output = form.selectbox("Scegli quale amenity vedere", ["bicycle_parking", "bicycle_rental", "bus_station", "car_rental", "car_sharing", 'charging_station', "fuel"])
        form.form_submit_button("Mostra")
        
        am = get_amenities(city=self.parametro, amenity_type=output).copy()
        fig2 = px.scatter_mapbox(am, lat="latitude", lon="longitude",
                        color_discrete_sequence=["black"], hover_data=['capacity'],
                        hover_name="operator", zoom=10,center=city_centroid[self.parametro])
        fig2.update_layout(mapbox_style="open-street-map")
        fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
        st.plotly_chart(fig2, use_container_width=True)

@st.cache
def get_amenities(isocode_country="IT", city="Roma", amenity_type="fast_food"):
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    overpass_query = '''
        [out:json];
        area["name"="'''+city+'''"];
        (
        node["amenity"="'''+amenity_type+'''"](area);
        );
        out center;
    '''

    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    records_list = list()
    for node in data["elements"]:
        record = dict()
        if "capacity" in node["tags"]:
            record["capacity"] = node["tags"]["capacity"]
        if "operator" in node["tags"]:
            record["operator"] = node["tags"]["operator"]
        record["id"] = node["id"]
        record["latitude"] = node["lat"]
        record["longitude"] = node["lon"]
        record["geometry"] = shapely.geometry.Point(record["longitude"], record["latitude"])
        records_list.append(record)
    return gpd.GeoDataFrame(records_list)


  