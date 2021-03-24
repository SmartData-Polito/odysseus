

# currentdir = os.path.dirname(os.path.realpath(__file__))
# parentdir = os.path.dirname(currentdir)
# parentparentdir = os.path.dirname(os.path.dirname(currentdir))
# p = os.path.join(parentparentdir,'e3f2s')
# sys.path.append(p)
# st.write(p)

from dashboards.load_data import *
import streamlit as st
from datetime import date
from e3f2s.city_data_manager.config.config import cities 


def load_sidebar():
    
    city_name = st.sidebar.selectbox(
        'City:',
        cities
    )

    st.sidebar.write(
        """ 
        # Hai scritto: {} """.format(city_name)
    )

    selected_month = st.sidebar.selectbox('Month', list(reversed(range(10, 13))))
    selected_year = st.sidebar.selectbox('Year', [2017])

    st.sidebar.write(
        """
        # Vista corrente
        """
    )
    current_view = st.sidebar.radio(
        'Seleziona la tua vista corrente:',
        ("CDM", "Demand", "Supply", "Simulator")
    )

    return current_view, city_name, selected_year, selected_month
