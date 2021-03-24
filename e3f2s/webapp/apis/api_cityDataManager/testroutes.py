from flask import Blueprint, jsonify, request
from e3f2s.webapp.emulate_module.city_data_manager import CityDataManager
import pymongo as pm
import json
import os
import random
random.seed(42)
from flask_cors import CORS
api_cdm = Blueprint('api_cdm', __name__)
CORS(api_cdm)

HOST = 'mongodb://localhost:27017/'
DATABASE = 'inter_test'
COLLECTION = 'plots'

def set_path():
    ROOT_DIR = os.path.abspath(os.curdir)
    cdm_data_path = os.path.join(
	    ROOT_DIR,
        "e3f2s/city_data_manager/",
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

def retrieve_per_city(path,level="norm",datatype = "trips",):
    data = {}
    print("PATH",path)
    for subdir, dirs, files in os.walk(path):
        for f in files:
            filepath = os.path.join(subdir,f)
            if level not in filepath or datatype not in filepath:
                continue
            elif level in filepath and filepath.endswith(".csv"):
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

@api_cdm.route('/simulate',methods=['POST'])
def simulate():
    """
    Receive the configuration from the front end and run simulation
    """
    print("Received post")
    request.get_data()
    data = json.loads(request.data)
    print(data)
    # f = open("sim_general_conf.py","w")
    # f.write("sim_general_conf_grid = "+ str(data))
    cities,years,months,data_source_ids = extract_params(data)
    cdm = CityDataManager(cities,years,months,data_source_ids)
    cdm.run()
    collection = initialize_mongoDB(HOST,DATABASE,COLLECTION)
    param_id="placeholder"
    query = {"_id":param_id}
    results = list(collection.find(query))
    return jsonify({'Result':"Success"})

@api_cdm.route('/available_data',methods=['GET'])
def run():
    print("Return available data per cities")
    level = request.args.get("level",default = 'norm')
    # cdm = CityDataManager()
    # cdm.run()
    summary = summary_available_data(level)
    print(summary)
    return jsonify(summary)

@api_cdm.route('/get-cdm-data',methods=['GET'])
def get_data(graph = 'all'):
    param_id = request.args.get("id",default = 'TEST')
    graph = request.args.get("graph",default = 'all')
    
    collection = initialize_mongoDB(HOST,DATABASE,COLLECTION)
    
    if graph == 'all':
        query = {"_id":param_id}
        results = list(collection.find(query))
    else:
        query = [{"$match": {"_id":param_id}}, {"$project": {"_id" : "$_id", graph: 1}}]
        results = list(collection.aggregate(query))
    print(results)
    return json.dumps(list(results))
    
@api_cdm.route('/available_data_test',methods=['GET'])
def bretest():

    risultato  = {
        "Torino": {
                "big_data_db": {
                    "2017": {
                        "10": random.randint(0,1000), 
                        "11": random.randint(0,1000), 
                        "12": random.randint(0,1000)
                    },
                    "2018": {
                        "10": random.randint(0,1000), 
                        "11": random.randint(0,1000), 
                        "12": random.randint(0,1000)
                    }
                },
                "checco_db": {
                    "2017": {
                        "10": random.randint(0,1000), 
                        "11": random.randint(0,1000), 
                        "12": random.randint(0,1000)
                    },
                    "2018": {
                        "10": random.randint(0,1000), 
                        "11": random.randint(0,1000), 
                        "12": random.randint(0,1000)
                    }
                }
        },
        "Milano": {
                "big_data_db": {
                    "2016": {
                        "10": random.randint(0,1000), 
                        "11": random.randint(0,1000), 
                        "12": random.randint(0,1000)
                    },
                    "2018": {
                        "10": random.randint(0,1000), 
                        "11": random.randint(0,1000), 
                        "12": random.randint(0,1000)
                    },
                },
                "checco_db": {
                    "2017": {
                        "10": random.randint(0,1000), 
                        "11": random.randint(0,1000), 
                        "12": random.randint(0,1000)
                    },
                    "2019": {
                        "10": random.randint(0,1000), 
                        "11": random.randint(0,1000), 
                        "12": random.randint(0,1000)
                    }
                }
            }
        }

        # risultato2 = {
        #     {
        #         "city":"Torino",
        #         "datasource":"bigdatadb",
        #         "values":
        #     },
        #     {

        #     }
        # }

    return jsonify(risultato)
