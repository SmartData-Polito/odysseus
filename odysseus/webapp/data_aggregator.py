import os
import datetime
import random
import geopandas as gpd
import pandas as pd
import pymongo as pm
import json
import numpy as np
from bson import json_util
from functools import reduce
import skmob
from skmob.tessellation import tilers
from skmob.preprocessing import detection

def get_out_flow_count(trips_origins):
    
    trips_origins["day"] = trips_origins['start_time'].dt.day
    #trips_origins["start_hour"] = trips_origins['start_time'].dt.hour
    out_flow_count = trips_origins[["tile_ID", "year", "month", "day", "start_time"]].groupby(
        ["tile_ID", "year", "month", "day"], as_index=False
    ).count().fillna(0.0).rename(columns={"start_time": "out_flow_count"})

    return out_flow_count

def get_in_flow_count(trips_destinations):
    
    trips_destinations["day"] = trips_destinations['end_time'].dt.day
    #trips_destinations["end_hour"] = trips_destinations['end_time'].dt.hour
    in_flow_count = trips_destinations[["tile_ID", "year", "month", "day", "end_time"]].groupby(
        ["tile_ID", "year", "month", 'day'], as_index=False
    ).count().rename(columns={"end_time": "in_flow_count"})

    return in_flow_count

def build_tesselation(park_df):
    df = park_df.copy()

    tdf = skmob.TrajDataFrame(park_df, latitude='start_latitude', longitude='start_longitude', user_id='plate', datetime='start_time')
    stdf = detection.stops(tdf, stop_radius_factor=0.5, minutes_for_a_stop=15.0, spatial_radius_km=0.2, leaving_time=True)

    stdf_parkings = stdf[['uid', 'end_time', 'end_longitude', 'end_latitude', 'leaving_datetime']].rename(columns={
        'end_time':'start_parking', 'end_longitude':'park_longitude', 'end_latitude':'park_latitude', 'leaving_datetime':'end_parking'
    })

    # grid using skmob tilers
    tessellation = tilers.tiler.get("squared", base_shape="Turin, Italy", meters=500)
    tessellation["tile_ID"] = tessellation.index.values
    return tessellation,stdf_parkings

def merge_spatial_df(data_frames,on_cols=['tile_ID', 'year', 'month', 'day']):
    ## Merge all together 
    df_merged = reduce(lambda left,right: pd.merge(left,right, how='outer', on = on_cols), data_frames).fillna(0)

    date_columns = ['year', 'month', 'day']
    df_merged['date'] = pd.to_datetime(df_merged[date_columns])
    df_merged = df_merged.drop(date_columns, axis=1)

    df_merged.set_index('date').sort_index()

    listed_data = pd.DataFrame()

    df_grouped_to_list = [df_merged.groupby(['date'])[['out_flow_count', 'tile_ID']].apply(lambda x: x.values.tolist()),
                df_merged.groupby(['date'])[['in_flow_count', 'tile_ID']].apply(lambda x: x.values.tolist()),
                df_merged.groupby(['date'])[['uid', 'tile_ID']].apply(lambda x: x.values.tolist())]
    a = pd.concat(df_grouped_to_list, axis=1)
    a = a.rename(columns={0: "out_flow_count", 1:"in_flow_count", 2:'origin_count'})
    return a

class DataAggregator:
    def __init__(self) -> None:
        pass

    def groupby_day_hour(self,filepath,city):
        cols = ["start_time","duration","euclidean_distance"]
        df = pd.read_csv(filepath,usecols=cols)
        df['start_time'] = pd.to_datetime(df['start_time'],utc=True).dt.to_pydatetime()
        df["occurance"] = 1
        df["year"] = df['start_time'].dt.year
        df["month"] = df['start_time'].dt.month
        df["day"] = df['start_time'].dt.day
        df["hour"] = df['start_time'].dt.hour
        count_df = df.groupby(["year","month","day","hour"]).agg(
            {"occurance":sum,"duration":[sum,"mean"],"euclidean_distance":[sum,"mean"]})
        ans = self.build_raw_answer_hour(count_df,city)
        return ans

    def build_raw_answer_hour(self,df,city,DEBUG=False):
        # Assume the df contains value for a single month
        final_dict = {}
        document = {"city":city}
        document_list=[]
        prev_hour = -1
        prev_day = 0
        year = 0
        month = 0
        for index, row in df.iterrows():
            year = index[0]
            month = index[1]
            #index[0] =year
            #index[1] = month
            #index[2] = day
            #index[3] = hour
            print("DAY: ",index)
            if index[0] in final_dict.keys() and index[1] in final_dict[index[0]].keys() and index[2] in final_dict[index[0]][index[1]].keys():
                #If there is a gap fill the gap
                if abs(prev_hour - index[3])> 1 and prev_day==index[2]:
                    for _ in range(1, abs(prev_hour - index[3]) ):
                        final_dict[index[0]][index[1]][index[2]][0].append(0) #n_booking
                        final_dict[index[0]][index[1]][index[2]][1].append(0) #avg_duration
                        final_dict[index[0]][index[1]][index[2]][2].append(0) #sum avg_duration
                        final_dict[index[0]][index[1]][index[2]][3].append(0) #euclidean_distance
                        final_dict[index[0]][index[1]][index[2]][4].append(0) #sum euclidean_distance
            elif index[0] in final_dict.keys() and index[1] in final_dict[index[0]].keys() :
                #Start a new day initialize it
                final_dict[index[0]][index[1]].update({index[2]:[[],[],[],[],[]]})
                #Fill previous day if not complete 24 hour
                for _ in range(0, abs(23 - prev_hour)):
                    final_dict[index[0]][index[1]][prev_day][0].append(0) #n_booking
                    final_dict[index[0]][index[1]][prev_day][1].append(0) #avg_duration
                    final_dict[index[0]][index[1]][prev_day][2].append(0) #sum avg_duration
                    final_dict[index[0]][index[1]][prev_day][3].append(0) #euclidean_distance
                    final_dict[index[0]][index[1]][prev_day][4].append(0) #sum euclidean_distance
                #Fill empty days
                for gg in range(1, abs(prev_day - index[2]) ):
                    empty_day = [0 for x in range(24)]
                    final_dict[index[0]][index[1]].update({prev_day+gg:[empty_day for x in range (5)]})
                #Fill current day up to first hour with data
                for _ in range(0,index[3]):
                    final_dict[index[0]][index[1]][index[2]][0].append(0) #n_booking
                    final_dict[index[0]][index[1]][index[2]][1].append(0) #avg_duration
                    final_dict[index[0]][index[1]][index[2]][2].append(0) #sum avg_duration
                    final_dict[index[0]][index[1]][index[2]][3].append(0) #euclidean_distance
                    final_dict[index[0]][index[1]][index[2]][4].append(0) #sum euclidean_distance
                # The previous day is complete -> upload to mongo
                for gg in range(0, abs(prev_day - index[2])):
                    # print(final_dict[index[0]][index[1]][prev_day+gg])
                    document.update({"year":year,"month":month,"day":prev_day+gg,
                                "n_booking":final_dict[index[0]][index[1]][prev_day+gg][0],
                                "avg_duration":final_dict[index[0]][index[1]][prev_day+gg][1],
                                "sum_duration":final_dict[index[0]][index[1]][prev_day+gg][2],
                                "euclidean_distance":final_dict[index[0]][index[1]][prev_day+gg][3],
                                "sum_euclidean_distance":final_dict[index[0]][index[1]][prev_day+gg][4]})
                    document_list.append(document)
                    document = {"city":city}
            else:
                final_dict.update({index[0]:{index[1]:{index[2]:[[],[],[],[],[]]}}})
                for _ in range(0,index[3]):
                    final_dict[index[0]][index[1]][index[2]][0].append(0) #n_booking
                    final_dict[index[0]][index[1]][index[2]][1].append(0) #avg_duration
                    final_dict[index[0]][index[1]][index[2]][2].append(0) #sum avg_duration
                    final_dict[index[0]][index[1]][index[2]][3].append(0) #euclidean_distance
                    final_dict[index[0]][index[1]][index[2]][4].append(0) #sum euclidean_distance
                    
            final_dict[index[0]][index[1]][index[2]][0].append(int(row["occurance"]))
            final_dict[index[0]][index[1]][index[2]][1].append(int(row["duration"]["mean"]))
            final_dict[index[0]][index[1]][index[2]][2].append(int(row["duration"]["sum"]))
            final_dict[index[0]][index[1]][index[2]][3].append(int(row["euclidean_distance"]["mean"]))
            final_dict[index[0]][index[1]][index[2]][4].append(int(row["euclidean_distance"]["sum"]))
            prev_hour = index[3]
            prev_day = index[2]
        document.update({"year":year,"month":month,"day":prev_day,"n_booking":final_dict[index[0]][index[1]][prev_day][0],
                                "avg_duration":final_dict[index[0]][index[1]][prev_day][1],
                                "sum_avg_duration":final_dict[index[0]][index[1]][prev_day][2],
                                "euclidean_distance":final_dict[index[0]][index[1]][prev_day][3],
                                "sum_euclidean_distance":final_dict[index[0]][index[1]][prev_day][4]})
        document_list.append(document)
        return document_list

    def spatial_grouping(self,datapath):
        # select columns needed for analysis and read csv
        cols = ["start_time", "end_time", 'start_longitude', 'start_latitude', 'end_longitude', 'end_latitude', 'plate']
        park_df = pd.read_csv(datapath, usecols=cols)
        park_df['start_time'] = pd.to_datetime(park_df['start_time'],utc=True).dt.to_pydatetime()
        park_df['end_time'] = pd.to_datetime(park_df['end_time'],utc=True).dt.to_pydatetime()   

        tessellation,stdf_parkings = build_tesselation(park_df)

        or_count=self.origin_count(stdf_parkings,tessellation)
        of_count=self.out_flow_count(park_df,tessellation)
        if_count=self.in_flow_count(park_df,tessellation)
        agg_df = merge_spatial_df([of_count,if_count,or_count])
        print("FINE")
        return agg_df

    def build_spatial_doc(self,agg_df,city,datasource):
        agg_df['city'] = city
        agg_df['data_source_id'] = datasource
        agg_df['day'] = agg_df.index.day
        agg_df['month'] = agg_df.index.month
        agg_df['year'] = agg_df.index.year
        agg_df = agg_df.reset_index(drop=True)

        j = json.loads(agg_df.to_json(orient='records'))
        return j

    def origin_count(self,stdf_parkings,tessellation):
        trips_park = gpd.GeoDataFrame(
        stdf_parkings, geometry=gpd.points_from_xy(stdf_parkings.park_longitude, stdf_parkings.park_latitude))
        trips_park.crs = "epsg:4326"

        trips_park = gpd.sjoin(
            trips_park,
            tessellation,
            how='left',
            op='intersects'
        )

        trips_park['start_parking'] = pd.to_datetime(trips_park['start_parking'],utc=True).dt.to_pydatetime()
        trips_park['end_parking'] = pd.to_datetime(trips_park['end_parking'],utc=True).dt.to_pydatetime()
        trips_park

        trips_park['year'] = trips_park['start_parking'].dt.year
        trips_park['month'] = trips_park['start_parking'].dt.month
        trips_park['day'] = trips_park['start_parking'].dt.day
        origin_value_count = trips_park.groupby(["tile_ID", "year", "month", "day"], as_index=False)['uid'].nunique()
        return origin_value_count

    def out_flow_count(self,df,tessellation):
        df_copy = df.copy()
        origin_df = df_copy[['start_time', 'start_longitude', 'start_latitude']]
        origin_df['year'] = origin_df['start_time'].dt.year
        origin_df['month'] = origin_df['start_time'].dt.month

        trips_origins = gpd.GeoDataFrame(
            origin_df, geometry=gpd.points_from_xy(origin_df.start_longitude, origin_df.start_latitude))
        trips_origins.crs = "epsg:4326"

        trips_origins = gpd.sjoin(
            trips_origins,
            tessellation,
            how='left',
            op='intersects'
        )

        out_flow_count = get_out_flow_count(trips_origins)
        out_flow_count = out_flow_count.sort_values(["year", "month", "day"]).reset_index(drop=True)
        return out_flow_count
    
    def in_flow_count(self,df,tessellation):
        df_copy = df.copy()
        destination_df = df_copy[['end_time', 'end_longitude', 'end_latitude']]
        destination_df['year'] = destination_df['end_time'].dt.year
        destination_df['month'] = destination_df['end_time'].dt.month

        trips_destinations = gpd.GeoDataFrame(
            destination_df, geometry=gpd.points_from_xy(destination_df.end_longitude, destination_df.end_latitude))
        trips_destinations.crs = "epsg:4326"

        trips_destinations = gpd.sjoin(
            trips_destinations,
            tessellation,
            how='left',
            op='intersects'
        )


        in_flow_count = get_in_flow_count(trips_destinations)
        in_flow_count = in_flow_count.sort_values(['year', 'month', 'day']).reset_index(drop=True)
        return in_flow_count

