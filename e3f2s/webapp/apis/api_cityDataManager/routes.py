from flask import Blueprint, jsonify, request
from e3f2s.webapp.emulate_module.city_data_manager import CityDataManager
import pymongo as pm
import json

api_cdm = Blueprint('api_cdm', __name__)

HOST = 'mongodb://localhost:27017/'
DATABASE = 'inter_test'
COLLECTION = 'plots'

def initialize_mongoDB(host,database,collection):
    client = pm.MongoClient(host)
    db = client[database]
    return db[collection]
    
@api_cdm.route('/config',methods=['POST'])
def config():
    print("Received post")
    data = request.get_json()
    print(data)
    f = open("sim_general_conf.py","w")
    f.write("sim_general_conf_grid = "+ str(data))
    return jsonify({'config':1})

@api_cdm.route('/run',methods=['GET','PUT','POST'])
def run():
    print("Start simulation")
    cdm = CityDataManager()
    cdm.run()
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
    

