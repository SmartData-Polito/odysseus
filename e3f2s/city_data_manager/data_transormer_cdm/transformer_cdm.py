import os
import pandas as pd
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
        df_plates = df.filter(["plate"], axis=1)
        df_plates["occurance"] = 1
        most_used = df_plates.groupby(by="plate").sum(["occurance"]).sort_values(by=["occurance"], ascending=[True])
        most_used = most_used.reset_index()
        
        transformed = makeitjson(most_used)

    elif filter_type == "busy_hours":
        df_busy = df.filter(["start_hour"], axis=1)
        df_busy["occurance"] = 1
        most_busy_hour = df_busy.groupby(by="start_hour").sum(["occurance"]).sort_values(by=["occurance"], ascending=[True])
        most_busy_hour = most_busy_hour.reset_index()

        transformed = makeitjson(most_busy_hour)


    return transformed


# filter_types = [
#         {"type":"most_used_cars","x-axis":"plate"},
#         {"type":"busy_hours","x-axis":"start_hour"}
#         ]
# filter_types = [
#         ("most_used_cars","plate"),
#         ("busy_hours","start_hour")
#         ]
# filter_types = [
#         {"most_used_cars":"plate"},
#         {"busy_hours":"start_hour"}
#         ]
filter_types = {
        "most_used_cars": {"name":"most_used_cars","x-axis":"plate", "labelx":"Plate", "labely":"Usage"},
        "busy_hours": {"name":"busy_hours","x-axis":"start_hour", "labelx":"Start Hour", "labely":"Total"}
}


# ppp = transform_cdm("Torino", "norm", "trips", "big_data_db", "2017", "10", ".csv", filter_type='most_used_cars')
ppp = transform_cdm("Torino", "norm", "trips", "big_data_db", "2017", "10", ".csv", filter_type=filter_types["busy_hours"]["name"])

def simplebarchart(data, info):
    df= pd.read_json(data,orient="index")
    fig = px.bar(df, x=info["x-axis"], y='occurance',
                    hover_data=['occurance'], color='occurance',
                labels={'occurance':info["labely"], info["x-axis"]:info["labelx"]}, height=400)
    return fig


gg = simplebarchart(ppp, filter_types["busy_hours"])
gg.show()

