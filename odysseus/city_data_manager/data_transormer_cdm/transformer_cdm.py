import os
import pandas as pd
import plotly.express as px


# ROOT_DIR = os.path.abspath(os.curdir) 

# cdm_path,_ = os.path.split(ROOT_DIR)

# root_data_path = os.path.join(
# 	cdm_path,
# 	"data"
# )
# # path_to__data_city_norm_trips_source_year_month_filetype = ''

# # path_to__data_city_odtrips_points_year_month_filetype = ''
# # path_to__data_city_odtrips_trips_year_month_filetype = ''

# # path_to__data_city_raw_geo_trips = ''

# # data_steps_ids = ["raw","norm","od_trips"]
# # data_type_ids = ["points","trips","weather","geo"]
# # data_source = ["big_data_db"]


# def makeitjson(usually_a_df): # can also be a series
#     result = usually_a_df.to_json(orient="index")
#     return result

# def transform_cdm(city, data_steps_id, data_type_id, data_source, year, month, filetype, *args, **kwargs):
#     transformed={}
#     if kwargs.get('filter_type', None):
#         filter_type = kwargs.get('filter_type', None)


#     path_to__data_city_norm_trips_source_year_month_filetype = os.path.join(
#         root_data_path, city, data_steps_id, data_type_id, data_source, year+"_"+month + filetype

#     )

#     df = pd.read_csv(path_to__data_city_norm_trips_source_year_month_filetype)
#     # the csv file has been saved with the index, which i do not want
#     df = df.drop(df.columns[0], axis=1)

#     if filter_type == "most_used_cars":
#         df_plates = df.filter(["plate"], axis=1)
#         df_plates["occurance"] = 1
#         most_used = df_plates.groupby(by="plate").sum(["occurance"]).sort_values(by=["occurance"], ascending=[True])
#         most_used = most_used.reset_index()
        
#         transformed = makeitjson(most_used)

#     elif filter_type == "busy_hours":
#         df_busy = df.filter(["start_hour"], axis=1)
#         df_busy["occurance"] = 1
#         most_busy_hour = df_busy.groupby(by="start_hour").sum(["occurance"]).sort_values(by=["occurance"], ascending=[True])
#         most_busy_hour = most_busy_hour.reset_index()

#         transformed = makeitjson(most_busy_hour)


#     return transformed


# # filter_types = [
# #         {"type":"most_used_cars","x-axis":"plate"},
# #         {"type":"busy_hours","x-axis":"start_hour"}
# #         ]
# # filter_types = [
# #         ("most_used_cars","plate"),
# #         ("busy_hours","start_hour")
# #         ]
# # filter_types = [
# #         {"most_used_cars":"plate"},
# #         {"busy_hours":"start_hour"}
# #         ]
# filter_types = {
#         "most_used_cars": {"name":"most_used_cars","x-axis":"plate", "labelx":"Plate", "labely":"Usage"},
#         "busy_hours": {"name":"busy_hours","x-axis":"start_hour", "labelx":"Start Hour", "labely":"Total"}
# }


# # ppp = transform_cdm("Torino", "norm", "trips", "big_data_db", "2017", "10", ".csv", filter_type='most_used_cars')
# ppp = transform_cdm("Torino", "norm", "trips", "big_data_db", "2017", "10", ".csv", filter_type=filter_types["busy_hours"]["name"])

# def simplebarchart(data, info):
#     df= pd.read_json(data,orient="index")
#     fig = px.bar(df, x=info["x-axis"], y='occurance',
#                     hover_data=['occurance'], color='occurance',
#                 labels={'occurance':info["labely"], info["x-axis"]:info["labelx"]}, height=400)
#     return fig


# gg = simplebarchart(ppp, filter_types["busy_hours"])
# gg.show()


##############################################################################################################
import pytz
import geopandas as gpd
import pandas as pd
import shapely

from odysseus.city_data_manager.config.config import *


class Loader:
    
    def __init__(self, city, data_source_id, year, month):
        
        self.city_name = city
        self.year = year
        self.month = month
        self.data_source_id = data_source_id

        self.trips = None
        self.trips_destinations = None
        self.trips_origins = None

        self.points_data_path = os.path.join(
            data_paths_dict[self.city_name]["od_trips"]["points"],
            data_source_id,
            "_".join([str(year), str(month)])
        )
        self.trips_data_path = os.path.join(
            data_paths_dict[self.city_name]["od_trips"]["trips"],
            data_source_id,
            "_".join([str(year), str(month)])
        )

        if self.city_name == "Roma" or self.city_name == "Torino" or self.city_name == "Milano":
            self.tz = pytz.timezone("Europe/Rome")
        elif self.city_name == "Amsterdam":
            self.tz = pytz.timezone("Europe/Amsterdam")
        elif self.city_name == "Madrid":
            self.tz = pytz.timezone("Europe/Madrid")
        elif self.city_name == "Berlin":
            self.tz = pytz.timezone("Europe/Berlin")
        elif self.city_name == "New_York_City":
            self.tz = pytz.timezone("America/New_York")
        elif self.city_name == "Vancouver":
            self.tz = pytz.timezone("America/Vancouver")
        elif self.city_name == "Louisville":
            self.tz = pytz.timezone("America/Kentucky/Louisville")
        elif self.city_name == "Minneapolis" or self.city_name == "Chicago":
            self.tz = pytz.timezone("America/Chicago")
        elif self.city_name == "Austin" or self.city_name == "Kansas City":
            self.tz = pytz.timezone("US/Central")
        elif self.city_name == "Norfolk":
            self.tz = pytz.timezone("US/Eastern")
        elif self.city_name == "Calgary":
            self.tz = pytz.timezone("Canada/Mountain")

    def read_data (self):

        path = os.path.join(
            self.trips_data_path,
            "trips.csv"
        )
        df_trips = pd.read_csv(path)
        df_trips['geometry'] = df_trips['geometry'].apply(shapely.wkt.loads)
        self.trips = gpd.GeoDataFrame(df_trips, geometry='geometry')

        path_og = os.path.join(
            self.points_data_path,
            "origins.csv"
        )
        df_og = pd.read_csv(path_og)
        df_og['geometry'] = df_og['geometry'].apply(shapely.wkt.loads)
        self.trips_origins = gpd.GeoDataFrame(df_og, geometry='geometry')

        path_dt = os.path.join(
            self.points_data_path,
            "destinations.csv"
        )
        df_dt = pd.read_csv(path_dt)
        df_dt['geometry'] = df_dt['geometry'].apply(shapely.wkt.loads)
        self.trips_destinations = gpd.GeoDataFrame(df_dt, geometry='geometry')

        self.trips_origins.crs = "epsg:4326"
        self.trips_destinations.crs = "epsg:4326"
        self.trips_origins["start_longitude"] = self.trips_origins.geometry.apply(lambda p: p.x)
        self.trips_origins["start_latitude"] = self.trips_origins.geometry.apply(lambda p: p.y)
        self.trips_destinations["end_longitude"] = self.trips_destinations.geometry.apply(lambda p: p.x)
        self.trips_destinations["end_latitude"] = self.trips_destinations.geometry.apply(lambda p: p.y)

        if self.city_name == 'Vancouver':
            self.trips = self.trips[self.trips.start_longitude < -122.9]
            self.trips = self.trips[self.trips.end_longitude < 0]
        elif self.city_name == 'Berlin':
            self.trips = self.trips[(self.trips.start_latitude > 51) & (self.trips.start_latitude < 53)]
            self.trips = self.trips[(self.trips.start_longitude > 12) & (self.trips.start_longitude < 14)]
            self.trips = self.trips[(self.trips.end_latitude > 51) & (self.trips.end_latitude < 53)]
            self.trips = self.trips[(self.trips.end_longitude > 12) & (self.trips.end_longitude < 14)]
        elif self.city_name == 'Kansas City':
            self.trips = self.trips[(self.trips.start_latitude > 38.95) & (self.trips.start_latitude < 39.20)]
            self.trips = self.trips[(self.trips.end_latitude > 38.95) & (self.trips.end_latitude < 39.20)]

        self.trips_origins = self.trips_origins.loc[self.trips.index]
        self.trips_destinations = self.trips_destinations.loc[self.trips.index]

        self.trips.start_time = pd.to_datetime(self.trips.start_time)
        self.trips_origins.start_time = self.trips.start_time
        self.trips.end_time = pd.to_datetime(self.trips.end_time)
        self.trips_destinations.end_time = self.trips.end_time

        return self.trips_origins, self.trips_destinations

