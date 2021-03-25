import pandas as pd
import streamlit as st

import os, sys
import streamlit as st
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentparentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.append(parentparentdir)

from odysseus.dashboards.load_data import *
from odysseus.dashboards.overview.get_widgets import *


from odysseus.city_data_manager.data_transormer_cdm.transformer_cdm import Loader

@st.cache(allow_output_mutation=True)
def load_origin_destination_data(citta, anno, mese, sorgente):
    # get inputs from streamlit for city, year, month, data_source
    print(citta, anno, mese, sorgente)
    gigi = Loader(city=citta, data_source_id=sorgente, year=anno, month=mese)
    df_origins, df_destinations =  gigi.read_data()

    return df_origins, df_destinations 
