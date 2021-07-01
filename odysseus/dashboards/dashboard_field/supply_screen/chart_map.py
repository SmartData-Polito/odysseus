from odysseus.dashboards.dashboard_field.dashboard_chart import DashboardChart
from odysseus.dashboards.dashboard_field.utils import st_functional_columns

from odysseus.dashboards import session_state as SessionState
from threading import Thread


import streamlit as st
from functools import partial

import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import shapely
from streamlit_plotly_events import plotly_events
import datetime 
from streamlit_folium import folium_static

class ChartMap(DashboardChart, Thread):

    def __init__(self, og_data, title, subtitle, grid, start, end, tipo="heatmap", parametro='Torino'):
        
        Thread.__init__(self)
        DashboardChart.__init__(self, title, name=title, subtitle=subtitle)
        self.og_data = og_data
        #self.dest_data = dest_data
        self.parametro=parametro
        self.tipo = tipo
        self.grid = grid        
        self.startDay = start
        self.endDay = end
        arg = [["selectbox", "Scegli grafico", ['out_flow_count', 'in_flow_count','origin_count']]]

        self.widget_list= [partial(st_functional_columns, arg)]

    def getmap(self, gdf):
        bottom = st.empty()
        fig = px.choropleth_mapbox(gdf,
                                geojson=gdf.geometry,
                                locations=gdf.tile_ID,
                                #color="zone_id",
                                opacity=0.5,
                                center={"lat": 45.116177, "lon": 7.742615},
                                mapbox_style="open-street-map",
                                zoom=10)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.update(layout_coloraxis_showscale=False)

        with bottom:
            a = plotly_events(fig, hover_event=False, override_width=1000, select_event=False)

        return a

    def show_amenities_map(self):
        a = self.getmap(self.grid)
        here = st.empty()
        here1 = st.empty()
        upbottom = st.empty()
        bottom = st.empty()
        here2 = st.empty()
        if a is not None and len(a) > 0 :
            here.title("Hai selezionato la zona "+str(a[0]["pointNumber"]))
            zona = self.grid[ self.grid["tile_ID"] == a[0]["pointNumber"]]
            #here1.dataframe(grid_csv[ self.grid["FID"] == a[0]["pointNumber"]])


            fig2 = px.choropleth_mapbox(zona,
                                    geojson=zona.geometry,
                                    locations=zona.tile_ID,
                                    #color="zone_id",
                                    opacity=0.5,
                                    center={"lat": zona.iloc[0].geometry.centroid.y, "lon": zona.iloc[0].geometry.centroid.x},
                                    mapbox_style="open-street-map",
                                    zoom=14)
            fig2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
            fig2.update(layout_coloraxis_showscale=False)

            form = st.form("aaaa")
            output = form.selectbox("Scegli quale amenity vedere", ["bicycle_parking", "bicycle_rental", "bus_station", "car_rental", "car_sharing", 'charging_station', "fuel"])
            form.form_submit_button("Mostra")
            print(type(output))
            am = get_amenities(city="Torino", amenity_type=output).copy()
            st.dataframe(am)
            am["in"] = am.geometry.within(zona.iloc[0].geometry)
            am = am[am["in"] == True]

            fig2.add_scattermapbox(lat=am.latitude, lon=am.longitude, below='', hoverinfo="text", text = am.name,
                                marker=go.scattermapbox.Marker(
                                    color="white",
                                    size=9
                                )
                                    )
            #fig2.update_layout(mapbox_style="open-street-map")
            #fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
            here2.plotly_chart(fig2)


            if not upbottom.button("Clicca per selezionare un'altra zona"):
                bottom.write("")


        else:
            here.title("Premi su una cella per vedere i dati relativi a quella zona")


@st.cache
def get_amenities(isocode_country="IT", city="Roma", amenity_type="fast_food"):
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    overpass_query = '''
        [out:json];
        area["name"="''' + city + '''"];
        (node["public_transport"="''' + amenity_type + '''"](area););
        out center;
    '''


    print(overpass_query)
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    print(data)
    records_list = list()
    for node in data["elements"]:
        record = dict()
        if "name" in node["tags"]:
            record["name"] = node["tags"]["name"]
        record["id"] = node["id"]
        record["latitude"] = node["lat"]
        record["longitude"] = node["lon"]
        record["geometry"] = shapely.geometry.Point(record["longitude"], record["latitude"])
        records_list.append(record)
    return gpd.GeoDataFrame(records_list)

  