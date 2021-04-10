from flask import Blueprint, jsonify, request, redirect, Response, make_response
from odysseus.webapp.emulate_module.city_data_manager import CityDataManager
import pymongo as pm
from odysseus.webapp.apis.api_cityDataManager.utils import *
import json
import os
from datetime import datetime
import random
import pandas as pd
random.seed(42)
from flask_cors import CORS
api_cdm = Blueprint('api_cdm', __name__)
CORS(api_cdm)

@api_cdm.route('/run_cdm', methods=['POST'])
def run_cdm():
    print("hey")
    """
    Receive the configuration from the front end and run simulation
    {
    "years": ["2017"],
    "months": ["8"],
    "cities": ["Torino"],
    "data_source_ids": ["big_data_db"]
    }
    """
    # request.get_data()
    # data = json.loads(request.data)
    # # f = open("sim_general_conf.py","w")
    # # f.write("sim_general_conf_grid = "+ str(data))
    # cities,years,months,data_source_ids = extract_params(data)
    
    
    # data received {'formData': {'cities': 'Milano', 'data_source_ids': 'big_data_db', 'years': '2016', 'months': '10'}}
    try:
        data = request.get_json()
        print("data received from the form", data)
        form_inputs = data["formData"]
        cities = []
        years = []
        months = []
        data_source_ids = []
        cities.append(form_inputs["cities"])
        years.append(form_inputs["years"])
        months.append(form_inputs["months"])
        data_source_ids.append(form_inputs["data_source_ids"])

        print("EXTRACTED DATA",cities,years,months,data_source_ids)

        cdm = CityDataManager(cities,years,months,data_source_ids)
        cdm.run()
        payload =   {
                "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"#"https://www.google.com"  # "http://127.0.0.1:8501"
                }
        code = 302
        response = make_response(jsonify(payload), code)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.status_code = 302
    except:
        payload =   {
                "error": "something went wrong"
                }
        code = 500
        response = make_response(jsonify(payload), code)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.status_code = 500
    return response



    
    # db stuff that we will use later (mikey mouse)
    # collection = initialize_mongoDB(HOST,DATABASE,COLLECTION)
    # param_id="placeholder"
    # query = {"_id":param_id}
    # results = list(collection.find(query))
    return jsonify({'Result':"Success"})

@api_cdm.route('/available_data',methods=['GET'])
def available_data():
    print("Return available data per cities")
    level = request.args.get("level", default = 'norm')
    #summary = summary_available_data(level)
    filename = os.path.join(
	    os.path.abspath(os.curdir),
        "odysseus","webapp","apis","api_cityDataManager",f"{level}-data.json"
        )
    with open(filename, 'r') as f:
            summary = json.load(f)
    print(summary)
    return jsonify(summary)

@api_cdm.route('/get-cdm-data',methods=['GET'])
def get_cdm_data(graph = 'all'):
    param_id = request.args.get("id",default = 'TEST')
    graph = request.args.get("graph",default = 'all')
    
    #collection = initialize_mongoDB(HOST,DATABASE,COLLECTION)
    
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
                },
                "brendan_db": {
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

    return jsonify(risultato)


@api_cdm.route('/config-test',methods=['GET','POST'])
def configTest():
    # data received {'formData': {'cities': 'Milano', 'data_source_ids': 'big_data_db', 'years': '2016', 'months': '10'}}
    try:
        data = request.get_json()
        print("data received from form", data)
        form_inputs = data["formData"]
        cities = form_inputs["city"]
        years = form_inputs["year"]
        months = form_inputs["month"]
        data_source_ids = form_inputs["source"]

    except:
        payload =   {
                "error": "something went wrong"
                }
        code = 404
        response = make_response(jsonify(payload), code)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.status_code = 404

    payload =   {
                "link": "http://127.0.0.1:8501" # "https://www.google.com"
                }
    code = 302
    response = make_response(jsonify(payload), code)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.status_code = 302

    return response
