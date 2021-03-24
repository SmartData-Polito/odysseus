import sys
import os
import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import plotly.graph_objects as go


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentparentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.append(parentparentdir)


sim_result_path = os.path.join(parentdir, 'simulator', 'results', 'Torino', 'multiple_runs', 'big_data_db_test',
                               'sim_booking_requests.csv')


@st.cache
def update_graph(start_date, end_date):
    df_sub = df

    df_sub = df[start_date:end_date]

    figure = go.Figure(data=go.Scatter(x=df_sub['date'], y=df_sub['n_vehicles_booked'], mode='lines'))

    return figure

@st.cache
def display_choropleth(candidate):
    fig = px.choropleth(
        df_geo, geojson=geojson, color=candidate,
        locations="district", featureidkey="properties.district",
        projection="mercator", range_color=[0, 6500])
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


# ---------- Import and clean data (importing csv into pandas)
df = pd.read_csv(sim_result_path, index_col=0, parse_dates=True)

df.index = pd.to_datetime(df['date'])

df_geo = px.data.election()
geojson = px.data.election_geojson()
candidates = df_geo.winner.unique()

# ------------------------------------------------------------------------------
# App layout and functions calls

st.title('Titolo a caso')
st.sidebar.title("Odysseus - City Planner")
st.sidebar.write("Here you can choose the options you want")
start_date = st.sidebar.date_input("Start date: ", value=None, min_value=date(2017, 10, 1),
                                   max_value=date(2017, 10, 31))
stop_date = st.sidebar.date_input("Stop date: ", value=None, min_value=date(2017, 10, 1), max_value=date(2017, 10, 31))

candidate = st.sidebar.radio("Candidate:", candidates)

st.plotly_chart(update_graph(start_date, stop_date), use_container_width=True)
st.plotly_chart(display_choropleth(candidate))
