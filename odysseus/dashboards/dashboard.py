import os, sys
import streamlit as st

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentparentdir = os.path.dirname(os.path.dirname(currentdir))
p = os.path.join(parentparentdir,'odysseus')
sys.path.append(p)

from odysseus.dashboards.sidebar import *
from odysseus.dashboards.overview.get_plot_data import *
from odysseus.dashboards.overview.get_plots_with_menu import *
#from e3f2s.utils.st_html_utils import _max_width_


def load_dashboard():
    st.set_page_config(layout="wide")
    # *** LOAD SIDEBAR AND DATA ***
    # from sidebar.py
    current_view, city_name, selected_year, selected_month, selected_source = load_sidebar()
    
    
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
        <p class="big-font">City: {}!</p>
        """.format(city_name),
        unsafe_allow_html=True
    )

    st.markdown(
        """
        General Purpose Settings
        """,
        unsafe_allow_html=True
    )
    
    # from get_widgets.py
    start, stop = load_slider_menu(selected_year, selected_month)
    st.write("Start Date: "+ str(start)+" End Date: "+str(stop))


    # st.markdown(
    #     """
    #     here will go the two columns with origin and destination data
    #     """,
    #     unsafe_allow_html=True
    # )

    # read the two csv files given the parameters chosen
    origins, destinations = get_bookings_count_plot_data(city_chosen=city_name,\
                                                        year_chosen=selected_year,\
                                                        month_chosen = selected_month,  
                                                        source_chosen =selected_source)


    # split the page into two columns to display origins and destinations
    col_lx, col_rx = st.beta_columns(2)

    col_lx.markdown(
        """
        Origins
        """,
        unsafe_allow_html=True
    )

    fig = plot_df(origins, "60Min", 'plate')
    col_lx.plotly_chart(fig, use_container_width=True)

    col_rx.markdown(
        """
        Destinations
        """,
        unsafe_allow_html=True
    )

    fig = plot_df(destinations, "60Min", 'plate')
    col_rx.plotly_chart(fig, use_container_width=True)
    # if bookings_count is not None:

    #     _max_width_()
    #     load_charts_with_menu(bookings_by_hour)


load_dashboard()