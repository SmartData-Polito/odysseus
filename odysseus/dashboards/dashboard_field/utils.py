from functools import partial
import git
import os
import streamlit as st
from odysseus.dashboards.dashboard_field.dashboard_screen import DashboardScreen

graph_types = [ "tamponi", "totali_principali", "nuovi_principali", "tassi_principali", "dettaglio_pazienti_attuali", "tassi_condizioni_cliniche"]
NUMERO_GRAFICI = len(graph_types)

graph_titles = [
    "Totale tamponi",
    "Totale principali",
    "Nuovi principali",
    "Tassi principali",
    "Dettaglio pazienti attuali",
    "Tassi condizioni cliniche"

]
graph_subtitles = [
    "Questo grafico mostra l'andamento temporale del numero di tamponi effettuati. Nello stesso grafico viene anche mostrato il numero totale di casi.",
    "Questo grafico mostra l'andamento temporale dei tre valori principali: attualmente positivi, deceduti e guariti.",
    "Questo grafico mostra le variazioni giornaliere dei nuovi positivi, degli attualmente positivi, dei deceduti e dei guariti.",
    "Questo grafico riporta i principali tassi (positivi, mortalità, tamponi positivi, mortalità).",
    "Questo grafico si focalizza su come sono distribuiti i positivi tra isolamento domiciliare, ricoverati e in terapia intensiva.",
    "Questo grafico si focalizza sui tassi dei pazienti in isolamento domiciliare, ricoverati e in terapia intensiva."

]
list_mesi = ["gennaio","febbraio","marzo","aprile","maggio","giugno", "luglio", "agosto", "settembre", "ottobre","novembre","dicembre"]

regioni = ["abruzzo", "basilicata", "calabria", "campania", "emilia-romagna", "friuliveneziagiulia", "lazio",
                   "liguria", "lombardia", "marche", "molise", "pabolzano", "patrento", "piemonte",
                   "puglia", "sardegna", "sicilia", "toscana", "umbria", "valledaosta", "veneto"]

articoli_regioni_no_in = { "lazio":"nel", "marche":"nelle", "pabolzano":"nella", "patrento":"nella"}

regioni_da_trasformare = {"emilia-romagna":"Emilia Romagna", "friuliveneziagiulia":"Friuli Venezia Giulia", "pabolzano":"Provincia Autonoma di Bolzano",
                          "patrento":"Provincia Autonoma di Trento", "valledaosta":"Valle d'Aosta"
                          }

@st.cache
def transform_regions_pc_to_human_all():
    ret = []
    for regione in regioni:
        if regione in regioni_da_trasformare:
            ret.append(regioni_da_trasformare[regione])
        else:
            ret.append(regione.capitalize())
    return ret


def transform_regions_pc_to_human(regione):
        if regione in regioni_da_trasformare:
            ret=regioni_da_trasformare[regione]
        else:
            ret=regione.capitalize()
        return ret

def transform_region_to_pc(region):
    for key in regioni_da_trasformare:
        if regioni_da_trasformare[key] == region:
            return key
    return region.lower()




## fare funzione wrapper a questa, che
# -pulla
# -calcola len della directory dati
# -chiama get_norm_data con parametro il numero di entry. Cosi se son le stesse di prima prende la versione cachata, altrimenti ne
# crea una nuova. Vedere la stessa cosa nel dizionario, mettendo come chiavi [len][regione][tipo] e se diz[len] è vuoto, svuotare tutto il rest
# directory: C:\User\franc\PycharmProjects\covid-19\covid_19\data_manager\data\raw\cases\italy\COVID-19\dati-andamento-nazionale
# ttl non penso servirà più, immagino sia una lru cache (male che vada la forziamo con functools)

def get_norm_data():

    pull()

    key = len(os.listdir(os.path.join(raw_cases_paths_dict["italy"],"dati-andamento-nazionale")))
    return get_norm_data_cached(key)



@st.cache(allow_output_mutation=True, max_entries=2)
def get_norm_data_cached(key):
    italy_cases_ds = ItalyCasesDataSource()
    italy_cases_ds.normalise()
    italy_cases_ds.save_norm()
    italy_cases_ds.load_norm()
    return italy_cases_ds

@st.cache
def determina_scelte(dati):
    scelte_ = list(dati)[6:]
    scelte_ret = []
    for scelta in scelte_:
        if scelta not in ["note", "note_test", "day_threshold_cases", "note_casi", "codice_nuts_1", "codice_nuts_2"]:
                scelte_ret.append(scelta)
    return scelte_ret


def st_functional_columns(lista, sizes=None):
       if sizes is None:
              cols = st.beta_columns(len(lista))
       elif len(sizes) != len(lista):

              raise ValueError("func and size must have the same length")
       else:
              cols = st.beta_columns(sizes)

       i = 0
       ret = []
       for el in lista:

              if len(el) == 0:
                  ret.append(None)
              else:
                  if el[0] == "write":
                         f = partial(cols[i].write, *el[1:])
                  elif el[0] == "beta_expander":
                         f = partial(cols[i].beta_expander, *el[1:])
                  elif el[0] == "selectbox":
                         f = partial(cols[i].selectbox, *el[1:])
                  elif el[0] == "slider":
                         f = partial(cols[i].slider, *el[1:])
                  elif el[0] == "multiselect":
                      f = partial(cols[i].multiselect, *el[1:])
                  elif el[0] == "date_input":
                      f = partial(cols[i].date_input, *el[1:])
                  elif el[0] == "number_input":
                      f = partial(cols[i].number_input, *el[1:])

                  ret.append(f())
              i += 1

       return ret



base_shapes = {
    "Torino": "Turin, Italy",
    "Milano": "Milan, Italy",
    "Firenze": "Florence, Italy",
    "Roma": "Rome, Italy",
    
    "Madrid": "Madrid, Spain",
               
    "Berlin": "Berlin, Germany",
    "Frankfurt": "Frankfurt, Germany",
    "Hamburg": "Hamburg, Germany",
    "Munchen": "Munchen, Germany",
    "Rheinland": "Rheinland, Germany",
    "Stuttgart": "Stuttgart, Germany",
               
    "Toronto": "Toronto, Canada",
    "Vancouver": "Vancouver, Canada",
    "Calgary": "Calgary, Canada",
    "Montreal": "Montreal, Canada",
    
    "Austin": "Austin, USA",
    "Washington": "Washington, USA",
    "Columbus": "Columbus, USA",
    "Denver": "Denver, USA",
    "New York City": "New York City, USA",
    "San Diego": "San Diego, USA",
    "Seattle": "Seattle, USA",
    "Amsterdam":"Amsterdam, Netherlands"}



city_centroid = {
    "Torino": {"lat": 45.116177 ,"lon": 7.742615},
    "Milano": {"lat": 45.464664 ,"lon": 9.188540},	
    "Firenze": {"lat": 43.769562 ,"lon":11.255814},
    "Roma": {"lat": 41.9027835 ,"lon": 12.4963655},
    
    "Madrid": {"lat": 40.416775 ,"lon": -3.703790},
               
    "Berlin": {"lat": 52.520008,"lon": 13.404954},
    "Frankfurt":{"lat":  50.110924 ,"lon": 8.682127},
    "Hamburg": {"lat": 53.551086 ,"lon": 9.993682},
    "Munchen": {"lat": 48.137154 ,"lon": 11.576124},
    #"Rheinland": {"lat": 45.464664 ,"lon": 9.188540},
    "Stuttgart": {"lat": 48.783333 ,"lon": 9.183333},
               
    "Toronto": {"lat":  43.651070,"lon":  -79.347015},
    "Vancouver": {"lat": 49.246292 ,"lon": -123.116226},
    "Calgary": {"lat":  51.049999,"lon": -114.066666},
    "Montreal": {"lat":  45.508888,"lon": -73.561668},
    
    "Austin": {"lat":  30.266666 ,"lon": -97.733330},
    "Washington": {"lat":  38.8951,"lon": -77.0364},
    "Columbus": {"lat": 39.983334 ,"lon": -82.983330},
    "Denver": {"lat": 39.742043 ,"lon": -104.991531},
    "New York City": {"lat": 40.730610 ,"lon":-73.935242 },
    "San Diego": {"lat": 32.715736 ,"lon":-117.161087 },
    "Seattle": {"lat": 47.608013 ,"lon":-122.335167 },
    "Amsterdam":{"lat": 52.377956 ,"lon": 4.897070}}