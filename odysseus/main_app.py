import os, sys
import streamlit as st


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
#parentparentdir = os.path.dirname(os.path.dirname(currentdir))
p = os.path.join(parentdir,'odysseus')
sys.path.append(p)
st.write(p)

from dashboards.sidebar import *
from odysseus.dashboards.overview.get_plot_data import * 
from odysseus.dashboards.overview.get_plots_with_menu import *

import webbrowser

def main():
    st.set_page_config(layout="wide")
    
    if st.button('DASHBOARD'):
        webbrowser.open_new_tab('http://localhost:8080')
    
    if st.button('REACT'):
        webbrowser.open_new_tab('http://localhost:3000')
    
main()