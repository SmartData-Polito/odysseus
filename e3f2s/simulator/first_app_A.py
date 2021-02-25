import streamlit as st
import numpy as np
import pandas as pd
import time
import datetime
import altair as alt

st.title('Input data simulator')

# sidebar for inputs
# sim_general_conf.py ################################################################################################

# select city
city = st.sidebar.multiselect(
    'City you want to run the simulation on:',
    ["Torino", "Milano", "Berlin", "Vancouver", "New_York_City", "Amsterdam", "Madrid", "Roma"],
    ["Torino"]
)

# select run mode
sim_run_mode = st.sidebar.radio(
    "What's your run mode of choice",       # box header
    ('single_run', 'multiple_run', 'other') # possible choices
)

# select database
data_source_id = st.sidebar.text_input(
    'DB name',      # box header
    'big_data_db'   # default choice
)

# select event
sim_technique = st.sidebar.radio(
    "Simulation technique",         # box header
    ('eventG', 'traceB', 'other')   # possible choices
)

# select scenario
sim_scenario_name = st.sidebar.text_input(
    'simulation scenario',  # box header
    'city_single_run_test'  # default choices
)

# Fleet general parameters
# select load_factor
const_load_factor = st.sidebar.number_input('What is the load factor?')

# Space general parameters
# select the dimension of the grid
bin_side_length = st.sidebar.number_input(
    'Which is the grid size? [m]',
    min_value=1,
    max_value=1000,
    value=10,
    step=10,
    format='%d'
)

# select zone factor
k_zones_factor = st.sidebar.number_input(
    'Zone_factor'
)

# Time parameters
# select start date
start_date = st.sidebar.date_input(
    'Start date for simulation',
    value=datetime.date(2016, 1, 1),
    min_value=datetime.date(2016, 1, 1),
    max_value=datetime.date(2019, 12, 31)
)

# select end date
end_date = st.sidebar.date_input(
    'End date for simulation',
    value=start_date,
    min_value=start_date,
    max_value=datetime.date(2019, 12, 31)
)

year_start = start_date.year
year_end = end_date.year
month_start = start_date.month
month_end = end_date.month




# Single_run_config.py #################################################################################################
# select rate factor
request_rate_factor = st.sidebar.number_input(
    'Request rate',     # box header
    value=0.5           # default value
)

# select fleet load factor
fleet_load_factor = st.sidebar.number_input(
    'Fleet load factor',    # box header
    value=1                 # default value
)

# select n of vehicles
n_vehicles = st.sidebar.number_input(
    'Number of vehicles',    # box header
    value=200                # default value
)

# select time estimation
time_estimation = st.sidebar.checkbox(
    'Time estimation',  # box header
    value=True          # default value
)

# select queuing
queueing = st.sidebar.checkbox(
    'Queueing', # box header
    value=True  # default value
)

# alpha policy ?

# select beta param
beta = st.sidebar.number_input(
    'beta',         # box header
    min_value=0,    # base value
    value=100       # default value
)

# select n of poles per vehicle
n_poles_n_vehicles_factor = st.sidebar.number_input(
    'Ratio between poles and vehicles', # box header
    min_value=0.01,                     # min value
    value=0.06                          # default value
)

# select if hub or not
hub = st.sidebar.checkbox(
    'Hub',
    value=False
)

# select the policy of the hub
hub_zone_policy = st.sidebar.radio(
    'Hub zone policy',
    ('num_parkings', 'other')
)

#
cps_placement_policy = st.sidebar.radio(
    'cps placement policy',
    ('num_parkings', 'other')
)

#
distributed_cps = st.sidebar.checkbox(
    'Distributed cps',
    value=True
)

#
system_cps = st.sidebar.checkbox(
    'System cps',
    value=True
)

#
cps_zones_percentage = st.sidebar.number_input(
    'Percentage of cps zones',
    min_value=0.00,
    max_value=1.00,
    step=0.01,
    value=0.2
)

# select if battery swap or not
battery_swap = st.sidebar.checkbox(
    'Battery swap',
    value=False
)

# select avg time to reach a pole
avg_reach_time = st.sidebar.number_input(
    'Average reach time [min]',
    value=20,
    min_value=0
)

# select av service time
avg_service_time = st.sidebar.number_input(
    'Average service time [min]',
    value=0,
    min_value=0
)

# select if relocation or not
relocation = st.sidebar.checkbox(
    'Relocation',
    value=False
)

# select relocation strategy
charging_relocation_strategy = st.sidebar.selectbox(
    'Charging relocation strategy',
    ['closest free', 'random', 'shortest queuing']
)

# select the number of workers (to relocate)
n_workers = st.sidebar.number_input(
    'Number of workers',
    value=1000,
    min_value=0
)

# select if user can contribute or not
user_contribution = st.sidebar.checkbox(
    'User_contribution',
    value=False)
# if yes, select the willingness
if user_contribution:
    willingness = st.sidebar.slider(
        'Willingess',
        min_value=0.00,
        max_value=1.00,
        step=0.01,
        value=0.00)

# select charging strategy
charging_strategy = st.sidebar.selectbox(
    'Charging strategy',
    ['reactive']
)

######################## PLOTS ###############################################
# df = pd.read_csv("2017_10.csv") #sono solo le prenotazioni avvenute il 1/11 da 00 a 01?!
#
# # PLOT durata vs nBookings
# startTimes = df['start_time'].to_frame()
# endTimes = df['end_time'].to_frame()
# stTimes = []
# etTimes = []
# durations = []
# err = []
# for i in range(len(startTimes)):
#
#     s = startTimes.values[i][0].split('+')
#     e = endTimes.values[i][0].split('+')
#
#     start = s[0]
#     end = e[0]
#
#     format = '%Y-%m-%d %H:%M:%S'
#     dur = datetime.strptime(end, format) - datetime.strptime(start, format)
#
#     if (dur.total_seconds()/60) < 0:
#         err.append([end, start])
#         df.drop([i], inplace = True)
#     else:
#         durations.append(dur.total_seconds()/60) #in minutes
#         stTimes.append(start)
#         etTimes.append(end)
#
# print(len(err), len(df), len(durations))
# df["start_time"] = stTimes
# df["end_time"] = etTimes
# df["duration"] = durations
# df
#
# durations.sort()
# #print(durations)
# counter = 0
# totals = len(durations)
# count = []
# for x in durations:
#     nBookings = durations.count(x)
#     count.append((nBookings / totals + counter))
#     counter = count[-1]  # always take last element
#
# durDF = pd.DataFrame({'ordered duration': durations,
#                    'nBookings per duration': count},
#                      index = durations)
#
# line_chart = alt.Chart(durDF).mark_line(interpolate='basis').encode(
#     alt.X('ordered duration', title='Rental duration [min]'),
#     alt.Y('nBookings per duration', title='Number of bookings'),
#     color='category:N'
# ).properties(
#     title='CDF, number of bookings per rental duration, 01-11-2017'
# )
# st.altair_chart(line_chart)
#print(durDF)

# PLOT histogram nBookings in slot
#devo dividere in blocchi orari (colonna del df chiamata start_hour e end_hour) e contare quante bookings nello slot
#divido in blocchi temporali di 3 ore ciascuno: 00-03...

# estraggo dal datafarme solo la porzione di df che contiene il valore x nella colonna selezionata
#df.loc[df['start_hour'] == 0]
#print(df.loc[df['start_hour'].isin(['0','1', '2'])])
