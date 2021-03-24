#from plotter.plotly_ import *
#from plotter.altair_ import *
#from dashboard.overview.get_widgets import *


def load_charts_with_menu(bookings_by_hour, bookings_count, deleted_bookings_count, bubble_plot_df):

    deleted_bookings_count_plot = plot_lines_t_altair(deleted_bookings_count)
    bubble_plot = plot_bubble_altair(bubble_plot_df.groupby(["hour", "weekday"], as_index=False).sum())

    st.markdown(
        """
        <p class="mid-small-font">Numero di prenotazioni nel periodo selezionato</p>
        """,
        unsafe_allow_html=True
    )

    st_cols = st.beta_columns((3, 1))
    chart_type = load_bookings_count_widgets(st_cols[1])
    if chart_type == "line":
        bookings_count_plot = plot_lines_t_altair(bookings_count)
    elif chart_type == "bar":
        annotations = st_cols[1].radio('Mostra valori', ['Sì', 'No'])
        bookings_count_plot = plot_bars_t_altair(bookings_count, annotations)

    st_cols[0].altair_chart(bookings_count_plot, use_container_width=True)

    st.markdown(
        """
        <p class="mid-small-font">Numero di prenotazioni raggruppate per orario e giorno della settimana</p>
        """,
        unsafe_allow_html=True
    )
    st.altair_chart(bubble_plot, use_container_width=True)

    st.markdown(
        """
        <p class="mid-small-font">Distribuzione prenotazioni per strutture, attività, ed utenti (età, sesso)</p>
        """,
        unsafe_allow_html=True
    )
    pies = plot_pies(bookings_by_hour)

    st_cols = st.beta_columns(2)
    st.markdown(
        """
        <style>
            .modebar{
                  display: none !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    st_cols[0].plotly_chart(pies[0], use_container_width=True)
    st_cols[0].plotly_chart(pies[2], use_container_width=True)
    st_cols[1].plotly_chart(pies[1], use_container_width=True)
    st_cols[1].plotly_chart(pies[3], use_container_width=True)

    st.markdown(
        """
        <p class="mid-small-font">Numero di cancellazioni nel periodo selezionato</p>
        """,
        unsafe_allow_html=True
    )
    st.altair_chart(deleted_bookings_count_plot, use_container_width=True)
