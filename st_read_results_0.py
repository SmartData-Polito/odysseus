import os

import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

odysseus_results_path = "odysseus/simulator/results"
available_cities = [d for d in os.listdir(odysseus_results_path) if d != ".DS_Store"]

st.title("Odysseus Results")

st.sidebar.header("Select Scenario")

selected_city = st.sidebar.selectbox("Select city:", available_cities)

odysseus_city_results_path = os.path.join(odysseus_results_path, selected_city)

available_sim_type = [d for d in os.listdir(odysseus_city_results_path) if d != ".DS_Store"]

selected_sim_type = st.sidebar.selectbox("Select simulation type:", available_sim_type)

odysseus_sim_path = os.path.join(odysseus_results_path, selected_city, selected_sim_type)

available_scenarios = [d for d in os.listdir(odysseus_sim_path) if d != ".DS_Store"]

selected_scenario = st.sidebar.selectbox("Select scenario:", available_scenarios)

st.header("Configurations used in this scenario")

sim_general_config = pd.read_csv(os.path.join(odysseus_sim_path, selected_scenario, "sim_general_config_grid.csv"))
sim_demand_config = pd.read_csv(os.path.join(odysseus_sim_path, selected_scenario, "demand_model_config_grid.csv"))
sim_supply_config = pd.read_csv(os.path.join(odysseus_sim_path, selected_scenario, "sim_scenario_config_grid.csv"))

with st.expander("General Run Configuration"):
    sim_general_config

with st.expander("Demand Model Configuration"):
    sim_demand_config

with st.expander("Supply Model Configuration"):
    sim_supply_config

st.header("Results")

sim_stats_df = pd.read_csv(os.path.join(odysseus_sim_path, selected_scenario, "sim_stats.csv"))

if selected_scenario == "scenario_A":
    sim_stats_df["lambda"] = sim_stats_df.requests_rate_factor * 4
elif selected_scenario == "scenario_B":
    sim_stats_df["lambda"] = sim_stats_df.requests_rate_factor

with st.expander("Click to see the full results dataframe"):
    sim_stats_df

st.header("Charts")

if selected_scenario == "scenario_A" or selected_scenario == "scenario_B":

    st.subheader("Unsatisfied Demand [%] VS Lambda")

    unsatisfied_by_n_vehicles = sim_stats_df[[
        "lambda", "percentage_unsatisfied", "n_vehicles_sim"
    ]]

    with st.expander("Click to see the dataframe used for the plot"):
        st.dataframe(unsatisfied_by_n_vehicles)

    altair_fig = alt.Chart(unsatisfied_by_n_vehicles).mark_line(
        point=alt.OverlayMarkDef(color="red")
    ).encode(
        x=alt.X('lambda', scale=alt.Scale(
            domain=[unsatisfied_by_n_vehicles["lambda"].min(), unsatisfied_by_n_vehicles["lambda"].max()]
        )),
        y='percentage_unsatisfied',
        color="n_vehicles_sim",
        tooltip=["lambda", "percentage_unsatisfied", "n_vehicles_sim"]
    ).properties(
        title="Unsatisfied Demand [%]",
        height=300
    ).interactive()
    altair_fig.configure_title(
        fontSize=20,
        # font='Courier',
        anchor='start',
        color='black'
    )

    st.altair_chart(altair_fig, use_container_width=True)

elif selected_scenario == "scenario_B1":

    sim_stats_df.charging_duration = sim_stats_df.charging_duration / 3600

    unsatisfied_by_charging_duration = sim_stats_df[[
        "charging_duration", "percentage_unsatisfied", "n_vehicles_sim"
    ]]

    with st.expander("Click to see the dataframe used for the plot"):
        st.dataframe(unsatisfied_by_charging_duration)

        @st.cache
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode('utf-8')


        csv = convert_df(unsatisfied_by_charging_duration)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='unsatisfied_by_charging_duration.csv',
            mime='text/csv',
        )

    altair_fig = alt.Chart(unsatisfied_by_charging_duration).mark_line(
        point=alt.OverlayMarkDef(color="red")
    ).encode(
        x=alt.X('charging_duration', scale=alt.Scale(
            domain=[unsatisfied_by_charging_duration["charging_duration"].min(),
                    unsatisfied_by_charging_duration["charging_duration"].max()]
        )),
        y='percentage_unsatisfied',
        color="n_vehicles_sim",
        tooltip=["charging_duration", "percentage_unsatisfied", "n_vehicles_sim"]
    ).properties(
        title="Unsatisfied Demand [%]",
        height=300
    ).interactive()
    altair_fig.configure_title(
        fontSize=20,
        # font='Courier',
        anchor='start',
        color='black'
    )

    st.altair_chart(altair_fig, use_container_width=True)