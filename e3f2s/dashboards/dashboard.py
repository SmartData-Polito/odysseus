import os, sys
import streamlit as st

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentparentdir = os.path.dirname(os.path.dirname(currentdir))
p = os.path.join(parentparentdir,'e3f2s')
sys.path.append(p)

from dashboards.sidebar import *
from dashboards.overview.get_plot_data import * 
from dashboards.overview.get_plots_with_menu import *
#from e3f2s.utils.st_html_utils import _max_width_


def load_dashboard():
    st.set_page_config(layout="wide")
    # *** LOAD SIDEBAR AND DATA ***
    #TODO
    current_view, city_name, selected_year, selected_month = load_sidebar()
    
    start, stop = load_slider_menu(selected_year, selected_month)
    st.write("Si parte da "+ str(start)+" si arriva a "+str(stop))

    # *** INTRO ***

    st.markdown(
        """
            <style>
            .big-font {
                font-size:80px !important;
            }

            .mid-small-font {
                font-size:40px !important;
            }

            </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p class="big-font">Città: {}!</p>
        """.format(city_name),
        unsafe_allow_html=True
    )
    st.markdown(
        """
        here will go the plots with the menu
        """,
        unsafe_allow_html=True
    )
    


    st.markdown(
        """
        here will go the two columns with origin and destination data
        """,
        unsafe_allow_html=True
    )

    origins,destinations = get_bookings_count_plot_data()



    col_og, col_dt = st.beta_columns(2)

    col_og.markdown(
        """
        Colonna 1 - Origins
        """,
        unsafe_allow_html=True
    )

    fig = plot_df(origins, "60Min", 'plate')
    col_og.plotly_chart(fig, use_container_width=True)

    col_dt.markdown(
        """
        Colonna 2 - Destinations
        """,
        unsafe_allow_html=True
    )

    fig = plot_df(destinations, "60Min", 'plate')
    col_dt.plotly_chart(fig, use_container_width=True)
    # if bookings_count is not None:

    #     _max_width_()
    #     load_charts_with_menu(bookings_by_hour)


load_dashboard()