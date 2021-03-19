from flask import Blueprint, jsonify, request
from e3f2s.webapp.emulate_module.city_data_manager import CityDataManager
import pymongo as pm
import json
import os

api_cdm = Blueprint('api_cdm', __name__)

HOST = 'mongodb://localhost:27017/'
DATABASE = 'inter_test'
COLLECTION = 'plots'

def set_path():
    ROOT_DIR = os.path.abspath(os.curdir)
    cdm_data_path = os.path.join(
	    ROOT_DIR,
        "e3f2s/city_data_manager/"
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

def summary_available_data():
    summary = {}
    path = set_path()
    print("PATH",path)
    for subdir, dirs, files in os.walk(path):
        print(subdir)
        for f in files:
            print(os.path.join(subdir,f))
    return

@api_cdm.route('/config',methods=['POST'])
def config():
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

@api_cdm.route('/run',methods=['GET','PUT','POST'])
def run():
    print("Start simulation")
    # cdm = CityDataManager()
    # cdm.run()
    summary_available_data()
    return jsonify({'Done':1})

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
    

