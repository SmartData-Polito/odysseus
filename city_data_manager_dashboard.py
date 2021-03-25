import os
import pandas as pd
import geopandas as gpd

import streamlit as st
st.set_page_config(layout="wide")

import shapely

city = st.sidebar.selectbox(
    'Which city do you wanna analyse?',
    ["Torino", "Milano"]
)

data_path = os.path.join(
    "odysseus", "city_data_manager", "data", city,
    "norm", "trips", "big_data_db", "2017_10.csv"
)

df = pd.read_csv(data_path)



st.title("City data manager dashboard")

origins = df.copy()
destinations = df.copy()

origins["geometry"] = df.apply(
    lambda x: shapely.geometry.Point(
        x["start_longitude"], x["start_latitude"]
    ), axis=1
)
destinations["geometry"] = df.apply(
    lambda x: shapely.geometry.Point(
        x["end_longitude"], x["end_latitude"]
    ), axis=1
)

origins = gpd.GeoDataFrame(origins)
destinations = gpd.GeoDataFrame(destinations)

st.write(df.head())

import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 1, figsize=(20, 5))

origins_plot = origins.plot(ax=ax)
st.write(fig)