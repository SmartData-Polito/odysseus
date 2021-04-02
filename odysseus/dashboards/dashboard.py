from odysseus.dashboards.sidebar import *
from odysseus.dashboards.overview.get_plot_data import *
from odysseus.dashboards.overview.get_plots_with_menu import *

from odysseus.dashboards.load_data import *
#from e3f2s.utils.st_html_utils import _max_width_
from streamlit_folium import folium_static
import folium

def load_dashboard():

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

    #get the dataframes based on sidebar choices
    origins, destinations = load_origin_destination_data(city_name, selected_year, selected_month, selected_source ) 

    # filter the daya based on widget (provisional)
    df_origin = filter_date(origins, str(start), str(stop), 'start_time')
    df_destinations = filter_date(destinations, str(start), str(stop), 'end_time')

    # st.markdown(
    #     """
    #     here will go the two columns with origin and destination data
    #     """,
    #     unsafe_allow_html=True
    # )

    # read the two csv files given the parameters chosen
    """ 
    plot_origins, plot_destinations = get_bookings_count_plot_data(city_chosen=city_name,\
                                                        year_chosen=selected_year,\
                                                        month_chosen = selected_month,  
                                                        source_chosen =selected_source)
    """
    
    # split the page into two columns to display origins and destinations
    col_lx, col_rx = st.beta_columns(2)

    col_lx.markdown(
        """
        Origins
        """,
        unsafe_allow_html=True
    )

    fig_origins = plot_df(df_origin, "60Min", 'plate')
    origins_map = get_bookings_map(city_name, df_origin, 'origin')
    busy_hours = get_bookings_by_hour(city_name,df_origin,start,stop,selected_source)
    col_lx.plotly_chart(busy_hours, use_container_width=True)
    col_lx.plotly_chart(fig_origins, use_container_width=True)
    with col_lx:
        
        folium_static(origins_map)

    col_rx.markdown(
        """
        Destinations
        """,
        unsafe_allow_html=True
    )
    
    fig_destinations = plot_df(df_destinations, "60Min", 'plate')
    destination_map = get_bookings_map(city_name, df_destinations, 'destination')
    busy_hours = get_bookings_by_hour(city_name,df_origin,start,stop,selected_source,"destination")
    col_rx.plotly_chart(busy_hours, use_container_width=True)
    col_rx.plotly_chart(fig_destinations, use_container_width=True)
    with col_rx:
        
        folium_static(destination_map)
    
    # if bookings_count is not None:

    #     _max_width_()
    #     load_charts_with_menu(bookings_by_hour)

    st.markdown(
        """
        <center class="mid-small-font">General Information on usage</center>
        """,
        unsafe_allow_html=True
    )
    most_used = get_most_used_cars(city_name,df_origin,start,stop,selected_source).update_layout(width=1500,height=600)
    st.write(most_used)


    avg_duration = get_average_duration(city_name,df_origin,start,stop,selected_source).update_layout(width=1500,height=600)
    st.write(avg_duration)

    # bubble_origins = bubble_plot(city_name,df_origin,start,stop,selected_source)#.update_layout(width=1500,height=600)
    # st.write(bubble_origins)