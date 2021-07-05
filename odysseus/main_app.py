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

# session_state = get(password='', username='')


# def generate_button_choice():
#     dashboard_button_block = st.empty()
#     react_button_block = st.empty()
#     dashboard_button = dashboard_button_block.button('DASHBOARD')
#     react_button = react_button_block.button('REACT')

#     if dashboard_button:
#         dashboard_button_block.empty()
#         react_button_block.empty()
#         load_dashboard()

#     if react_button:
#         webbrowser.open_new_tab('http://localhost:3000')


# if not is_authenticated(session_state.username, session_state.password):
#     login_blocks = generate_login_block()
#     username, password = login(login_blocks)
#     session_state.username = username
#     session_state.password = password
#     if is_authenticated(username, password):
#         clean_blocks(login_blocks)
#         generate_button_choice()
#     elif session_state.password != '':
#         st.error(
#             """
#             Username or password not recognised.
#             Please try again.
#             """
#         )
# else:
#     load_dashboard()

load_dashboard()