import os
import datetime
import random
import pandas as pd
import pymongo as pm
import json
import numpy as np
from bson import json_util

class DataAggregator:
    def __init__(self) -> None:
        pass

    def groupby_day_hour(self,filepath,city):
        cols = ["start_time","duration"]
        df = pd.read_csv(filepath,usecols=cols)
        df['start_time'] = pd.to_datetime(df['start_time'],utc=True).dt.to_pydatetime()
        df["occurance"] = 1
        df["year"] = df['start_time'].dt.year
        df["month"] = df['start_time'].dt.month
        df["day"] = df['start_time'].dt.day
        df["hour"] = df['start_time'].dt.hour
        count_df = df.groupby(["year","month","day","hour"]).agg({"occurance":sum,"duration":"mean"})
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
            elif index[0] in final_dict.keys() and index[1] in final_dict[index[0]].keys() :
                #Start a new day initialize it
                final_dict[index[0]][index[1]].update({index[2]:[[],[]]})
                #Fill previous day if not complete 24 hour
                for _ in range(0, abs(23 - prev_hour)):
                    print(final_dict)
                    final_dict[index[0]][index[1]][prev_day][0].append(0) #n_booking
                    final_dict[index[0]][index[1]][prev_day][1].append(0) #avg_duration
                #Fill empty days
                for gg in range(1, abs(prev_day - index[2]) ):
                    empty_day = [0 for x in range(24)]
                    final_dict[index[0]][index[1]].update({prev_day+gg:[empty_day,empty_day]})
                #Fill current day up to first hour with data
                for _ in range(0,index[3]):
                    final_dict[index[0]][index[1]][index[2]][0].append(0) #n_booking
                    final_dict[index[0]][index[1]][index[2]][1].append(0) #avg_duration
                # The previous day is complete -> upload to mongo
                for gg in range(0, abs(prev_day - index[2])):
                    document.update({"year":year,"month":month,"day":prev_day+gg,
                                "n_booking":final_dict[index[0]][index[1]][prev_day+gg][0],
                                "avg_duration":final_dict[index[0]][index[1]][prev_day+gg][1]})
                    document_list.append(document)
                    document = {"city":city}
            else:
                final_dict.update({index[0]:{index[1]:{index[2]:[[],[]]}}})
                for _ in range(0,index[3]):
                    final_dict[index[0]][index[1]][index[2]][0].append(0) #n_booking
                    final_dict[index[0]][index[1]][index[2]][1].append(0) #avg_duration
                    
            final_dict[index[0]][index[1]][index[2]][0].append(int(row["occurance"]))
            final_dict[index[0]][index[1]][index[2]][1].append(int(row["duration"]))
            prev_hour = index[3]
            prev_day = index[2]
        document.update({"year":year,"month":month,"day":prev_day,"n_booking":final_dict[index[0]][index[1]][prev_day][0],
                                "avg_duration":final_dict[index[0]][index[1]][prev_day][1]})
        document_list.append(document)
        return document_list
