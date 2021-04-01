import streamlit as st
st.set_page_config(layout="wide")

import os, sys
import webbrowser

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
for module_dir in os.listdir(parentdir):
    sys.path.append(os.path.join(parentdir, module_dir))

from odysseus.dashboards.session_state import get
from odysseus.login.login import *
from odysseus.dashboards.dashboard import *

session_state = get(password='', username='')

st.markdown(
        """
            <style>
            .big-font {
                font-size:80px !important;
            }

            .mid-small-font {
                font-size:40px !important;
            }

            .small-font {
                font-size:30px !important;
            }

            </style>
        """,
        unsafe_allow_html=True
    )
def generate_button_choice(username):
    st.markdown(
        """
        <p class="big-font">Welcome: {}!</p>
        """.format(username),
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p class="mid-small-font">Please choose the service:</p>
        """,
        unsafe_allow_html=True
    )
    colWidthArray=[1,1]
    expander1Array,expander2Array=[],[]
    col1,col2= st.beta_columns(colWidthArray)
    with col1:
        st.markdown(
        """
        <p class="small-font">Data Analysis</p>
        """,
        unsafe_allow_html=True
        )
        info = st.beta_expander("+")
        with info:
              st.markdown("""*
              Go Directly to the analysis of data already available 
              *""")
        #dashboard_button_block = st.empty()
    with col2:
        st.markdown(
        """
        <p class="small-font">Simulator</p>
        """,
        unsafe_allow_html=True
        )
        info = st.beta_expander("+")
        with info:
              st.markdown("""*
              Go to city data manager interface to run custom simulations
              *""")
        #react_button_block = st.empty()

    col1,col2,col3,col4,col5,col6= st.beta_columns([1 for x in range(6)])
    with col2:
        dashboard_button_block = st.empty()
    with col5:
        react_button_block = st.empty()
    dashboard_button = dashboard_button_block.button('GO Stramlit!')
    react_button = react_button_block.button('GO React!')

    if dashboard_button:
        dashboard_button_block.empty()
        react_button_block.empty()
        load_dashboard()

    if react_button:
        webbrowser.open_new_tab('http://localhost:3000')


if not is_authenticated(session_state.username, session_state.password):
    login_blocks = generate_login_block()
    username, password = login(login_blocks)
    session_state.username = username
    session_state.password = password
    if is_authenticated(username, password):
        clean_blocks(login_blocks)
        generate_button_choice(username)
    elif session_state.password != '':
        st.error(
            """
            Username or password not recognised.
            Please try again.
            """
        )
else:
    generate_button_choice(session_state.username)

