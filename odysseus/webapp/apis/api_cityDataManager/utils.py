import os
from datetime import datetime
import random
import pandas as pd
import pymongo as pm
import json
from bson import json_util

HOST = 'mongodb://localhost:27017/'
DATABASE = 'inter_test'
COLLECTION = 'test'

def set_path(api):
    ROOT_DIR = os.path.abspath(os.curdir)
    cdm_data_path = os.path.join(
	    ROOT_DIR,
        f"odysseus/{api}/",
	    "data"
    )
    return cdm_data_path

def initialize_mongoDB(host=HOST,database=DATABASE,collection=COLLECTION):
    client = pm.MongoClient(host)
    db = client[database]
    col = db[collection]
    return db,col

def extract_params (body):
    cities = body["cities"]
    years = body["years"]
    months = body["months"]
    data_source_ids = body["data_source_ids"]
    return cities,years,months,data_source_ids

def count_trips(filename):
    with open(filename,"rb") as f:
        return sum(1 for line in f)

def extract_format(filepath):
    source,name = os.path.split(os.path.splitext(filepath)[0])
    _,data_source_id = os.path.split(source)
    names_list = name.split("_")
    if len(names_list)<=2:
        year = names_list[0]
        month = names_list[1]
        return data_source_id,year,month
    else:
        city = "_".join([n for n in names_list[1:]])
        return data_source_id,"",city

def groupby_month(filepath):
    cols = ["init_time"]
    df = pd.read_csv(filepath,usecols=cols)
    df['init_time'] = pd.to_datetime(df['init_time'], unit='s').dt.to_pydatetime()
    df["occurance"] = 1
    df["year"] = df['init_time'].dt.year
    df["month"] = df['init_time'].dt.month
    count_df = df.groupby(["year","month"]).sum(["occurance"])
    ans = build_raw_answer(count_df)
    return ans

def groupby_day_hour(filepath):
    cols = ["start_time"]
    df = pd.read_csv(filepath,usecols=cols)
    df['start_time'] = pd.to_datetime(df['start_time'],utc=True).dt.to_pydatetime()
    df["occurance"] = 1
    df["year"] = df['start_time'].dt.year
    df["month"] = df['start_time'].dt.month
    df["day"] = df['start_time'].dt.day
    df["hour"] = df['start_time'].dt.hour
    count_df = df.groupby(["year","month","day","hour"]).sum(["occurance"])
    ans = build_raw_answer_hour(count_df)
    return ans

def build_raw_answer(df,DEBUG=False):
    final_dict = {}
    for index, row in df.iterrows():
        if index[0] in final_dict.keys():
            final_dict[index[0]].update({index[1]:int(row["occurance"])})
        else:
            final_dict.update({index[0]:{index[1]:int(row["occurance"])}})
    if DEBUG:
        print(final_dict)
    return final_dict

def build_raw_answer_hour(df,DEBUG=False):
    final_dict = {}
    prev_hour = -1
    prev_day = 0
    for index, row in df.iterrows():
        #index[0] =year
        #index[1] = month
        #index[2] = day
        #index[3] = hour
        print("DAY: ",index)
        if index[0] in final_dict.keys() and index[1] in final_dict[index[0]].keys() and index[2] in final_dict[index[0]][index[1]].keys():
            if index[2]!=1:
                if len(final_dict[index[0]][index[1]][index[2]-1])!=24:
                    print(final_dict[index[0]][index[1]][index[2]-1])
                    a=1/0
            if abs(prev_hour - index[3])> 1 and prev_day==index[2]:
                for _ in range(1, abs(prev_hour - index[3]) ):
                    final_dict[index[0]][index[1]][index[2]].append(0)
            # else:
            #     final_dict[index[0]][index[1]][index[2]].append(int(row["occurance"]))  
            
        elif index[0] in final_dict.keys() and index[1] in final_dict[index[0]].keys() :
            final_dict[index[0]][index[1]].update({index[2]:[]})
            for _ in range(0, abs(23 - prev_hour)):
                final_dict[index[0]][index[1]][prev_day].append(0)
            for gg in range(1, abs(prev_day - index[2]) ):
                michael_jordan_zeros = [0 for x in range(24)]
                final_dict[index[0]][index[1]].update({prev_day+gg:michael_jordan_zeros})
            for _ in range(0,index[3]):
                final_dict[index[0]][index[1]][index[2]].append(0)
            #final_dict[index[0]][index[1]][index[2]].append(int(row["occurance"]))

        elif index[0] in final_dict.keys() :
            final_dict[index[0]].update({index[1]:{index[2]:[]}})
            for _ in range(0,index[3]):
                final_dict[index[0]][index[1]][index[2]].append(0)
            #final_dict[index[0]][index[1]][index[2]].append([int(row["occurance"])])
        else:
            final_dict.update({index[0]:{index[1]:{index[2]:[]}}})
            for _ in range(0,index[3]):
                final_dict[index[0]][index[1]][index[2]].append(0)
        final_dict[index[0]][index[1]][index[2]].append(int(row["occurance"]))
        prev_hour = index[3]
        prev_day = index[2]

    db,col = initialize_mongoDB()
    id_object = col.insert_one(json.loads(json_util.dumps(final_dict)))
    return final_dict

def retrieve_per_city(path,level="norm",datatype = "trips",aggregate_level="month",DEBUG=False):
    data = {}
    if DEBUG:
        print("PATH",path)
    for subdir, dirs, files in os.walk(path):
        for f in files:
            filepath = os.path.join(subdir,f)
            if os.path.join(level,datatype,"big_data_db") not in filepath:
                continue

            elif level=="norm" and filepath.endswith(".csv"):
                if DEBUG:
                    print("FILEPATH: ",filepath)
                data_source_id,year,month = extract_format(filepath)
                if aggregate_level =="month":
                    number_trips = count_trips(filepath)
                #if data source already added append to current data structure
                if data_source_id in data.keys():
                    # if year is not already present append dictionary
                    if year not in data[data_source_id].keys():
                        data[data_source_id][year] = {month:number_trips}
                    else:
                        data[data_source_id][year][month] = number_trips
                else:
                    data[data_source_id] = {year : {month:number_trips}}

            elif level=="raw" and filepath.endswith(".csv"):
                if DEBUG:
                    print("FILEPATH: ",filepath)
                data_source_id,_,city = extract_format(filepath)
                if aggregate_level=="month":
                    months_collects = groupby_month(filepath)
                data[data_source_id] = months_collects
    if DEBUG:
        print(data)
    return data

def retrieve_per_city_per_hour(city,path,level="od_trips",datatype = "trips",data_source_id="big_data_db",DEBUG=False):
    data = {}
    if DEBUG:
        print("PATH",path)
    for subdir, dirs, files in os.walk(path):
        for f in files:
            filepath = os.path.join(subdir,f)
            if os.path.join(level,datatype,data_source_id) not in filepath:
                continue

            elif level=="od_trips" and filepath.endswith(".csv"):
                if DEBUG:
                    print("FILEPATH: ",filepath)
                #data_source_id,_,city = extract_format(filepath)
                day_collect = groupby_day_hour(filepath)
                data[data_source_id] = day_collect
    if DEBUG:
        print(data)
    return data

def summary_available_data(level='norm',api="city_data_manager",DEBUG=False):
    summary = {}
    # Get list of cities
    path = set_path(api)
    list_subfolders_with_paths = [f.path for f in os.scandir(path) if f.is_dir()]
    avalaible_cities = [os.path.basename(os.path.normpath(c)) for c in list_subfolders_with_paths]
    for paths,city in zip(list_subfolders_with_paths,avalaible_cities):
        data = retrieve_per_city(paths,level=level,DEBUG=DEBUG)
        summary[city] = data
    return summary

def summary_available_data_per_hour(level='od_trips',api="city_data_manager",DEBUG=False):
    summary = {}
    # Get list of cities
    path = set_path(api)
    list_subfolders_with_paths = [f.path for f in os.scandir(path) if f.is_dir()]
    avalaible_cities = [os.path.basename(os.path.normpath(c)) for c in list_subfolders_with_paths]
    for paths,city in zip(list_subfolders_with_paths,avalaible_cities):
        data = retrieve_per_city_per_hour(city,paths,level=level,DEBUG=DEBUG)
        summary[city] = data
    return summary

def create_predefined_file(formato=["norm","raw"],DEBUG=False):
    for f in formato:
        summary = summary_available_data(f,DEBUG=DEBUG)
        filename = os.path.join(
	    os.path.abspath(os.curdir),
        "odysseus","webapp","apis","api_cityDataManager",f"{f}-data.json"
        )
        with open(filename, 'w+') as f:
            json.dump(summary, f) 