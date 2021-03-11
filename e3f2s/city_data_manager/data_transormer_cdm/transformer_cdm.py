import os
import pandas as pd
import json
import plotly.express as px


ROOT_DIR = os.path.abspath(os.curdir) 

cdm_path,_ = os.path.split(ROOT_DIR)

root_data_path = os.path.join(
	cdm_path,
	"data"
)
# path_to__data_city_norm_trips_source_year_month_filetype = ''

# path_to__data_city_odtrips_points_year_month_filetype = ''
# path_to__data_city_odtrips_trips_year_month_filetype = ''

# path_to__data_city_raw_geo_trips = ''

# data_steps_ids = ["raw","norm","od_trips"]
# data_type_ids = ["points","trips","weather","geo"]
# data_source = ["big_data_db"]

# filter_type = ["most_used_cars"], all possible options 

def makeitjson(usually_a_df): # can also be a series
    result = usually_a_df.to_json(orient="index")
    return result

def transform_cdm(city, data_steps_id, data_type_id, data_source, year, month, filetype, *args, **kwargs):
    transformed={}
    if kwargs.get('filter_type', None):
        filter_type = kwargs.get('filter_type', None)


    path_to__data_city_norm_trips_source_year_month_filetype = os.path.join(
        root_data_path, city, data_steps_id, data_type_id, data_source, year+"_"+month + filetype

    )

    df = pd.read_csv(path_to__data_city_norm_trips_source_year_month_filetype)
    # the csv file has been saved with the index, which i do not want
    df = df.drop(df.columns[0], axis=1)

    if filter_type == "most_used_cars":
        #most_used = df["plate"].value_counts(ascending=False) # is a 'pandas.core.series.Series'
        df_plates = df.filter(["plate"], axis=1)
        df_plates["occurance"] = 1
        most_used = df_plates.groupby(by="plate").sum(["occurance"]).sort_values(by=["occurance"], ascending=[True])
        most_used = most_used.reset_index()
        
        transformed = makeitjson(most_used)

    return transformed


ppp = transform_cdm("Torino", "norm", "trips", "big_data_db", "2017", "10", ".csv", filter_type='most_used_cars')


def simplebarchart(data):
    df= pd.read_json(data,orient="index")
    fig = px.bar(df, x='plate', y='occurance',
                    hover_data=['occurance'], color='occurance',
                labels={'occurance':'Usage'}, height=400)
    return fig


gg = simplebarchart(ppp)
gg.show()

