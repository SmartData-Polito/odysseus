import os
from datetime import datetime
import random
import pandas as pd
import pymongo as pm


HOST = 'mongodb://localhost:27017/'
DATABASE = 'inter_test'
COLLECTION = 'plots'

def set_path():
    ROOT_DIR = os.path.abspath(os.curdir)
    cdm_data_path = os.path.join(
	    ROOT_DIR,
        "odysseus/city_data_manager/",
	    "data"
    )
    return cdm_data_path

def initialize_mongoDB(host,database,collection):
    client = pm.MongoClient(host)
    db = client[database]
    return db[collection]

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
    year,month = name.split("_")
    return data_source_id,year,month

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

def build_raw_answer(df):
    final_dict = {}
    for index, row in df.iterrows():
        if index[0] in final_dict.keys():
            final_dict[index[0]].update({index[1]:int(row["occurance"])})
        else:
            final_dict.update({index[0]:{index[1]:int(row["occurance"])}})
    print(final_dict)
    return final_dict

def retrieve_per_city(path,level="norm",datatype = "trips",):
    data = {}
    print("PATH",path)
    for subdir, dirs, files in os.walk(path):
        for f in files:
            filepath = os.path.join(subdir,f)
            if level not in filepath or datatype not in filepath:
                continue

            elif level=="norm" and filepath.endswith(".csv"):
                print("FILEPATH: ",filepath)
                data_source_id,year,month = extract_format(filepath)
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
                print("FILEPATH: ",filepath)
                data_source_id,_,city = extract_format(filepath)

                months_collects = groupby_month(filepath)
                data[data_source_id] = months_collects
    print(data)
    return data

def summary_available_data(level='norm'):
    summary = {}
    # Get list of cities
    path = set_path()
    list_subfolders_with_paths = [f.path for f in os.scandir(path) if f.is_dir()]
    avalaible_cities = [os.path.basename(os.path.normpath(c)) for c in list_subfolders_with_paths]
    for paths,city in zip(list_subfolders_with_paths,avalaible_cities):
        data = retrieve_per_city(paths,level=level)
        summary[city] = data
    return summary
