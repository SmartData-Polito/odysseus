from flask import Blueprint, jsonify, request,make_response
from odysseus.webapp.emulate_module.city_data_manager import CityDataManager
from odysseus.webapp.apis.api_cityDataManager.utils import *
import pymongo as pm
import json
import os
from datetime import datetime
import random
import pandas as pd
random.seed(42)
from flask_cors import CORS
api_cdm = Blueprint('api_cdm', __name__)
CORS(api_cdm)

HOST = 'mongodb://localhost:27017/'
DATABASE = 'inter_test'
COLLECTION = 'bookings_per_hour'

@api_cdm.route('/run_cdm',methods=['POST'])
def run_cdm():
    """
    Receive the configuration from the front end and run simulation
    """
    # data received {'formData': {'cities': 'Milano', 'data_source_ids': 'big_data_db', 'years': '2016', 'months': '10'}}
    try:
        data = request.get_json(force=True)
        print("data received from the form", data)
        form_inputs = data["formData"]
        cities = []
        years = []
        months = []
        data_source_ids = []
        if type(form_inputs["cities"])==list:
            cities = form_inputs["cities"]
        else:
            cities.append(form_inputs["cities"])
        if type(form_inputs["years"])==list:
            years = form_inputs["years"]
        else:
            years.append(form_inputs["years"])
        if type(form_inputs["months"])==list:
            months = form_inputs["months"]
        else:
            months.append(form_inputs["months"])
        if type(form_inputs["data_source_ids"])==list:
            data_source_ids = form_inputs["data_source_ids"]
        else:
            data_source_ids.append(form_inputs["data_source_ids"])

        print("EXTRACTED DATA",cities,years,months,data_source_ids)

        cdm = CityDataManager(cities,years,months,data_source_ids)
        cdm.run()
        payload =   {
                "link": "http://127.0.0.1:8501"
                }
        code = 302
        response = make_response(jsonify(payload), code)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.status_code = 302

        create_predefined_file()

    except Exception as e:
        print(e)
        payload =   {
                "error": "something went wrong "
                }
        code = 500
        response = make_response(jsonify(payload), code)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.status_code = 500
    return response
    # Collect from mongo
    # collection = initialize_mongoDB(HOST,DATABASE,COLLECTION)
    # param_id="placeholder"
    # query = {"_id":param_id}
    # results = list(collection.find(query))
    #return jsonify({'Result':"Success"})


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
def get_data():
    param_id = request.args.get("id",default = 'TEST')
    graph = request.args.get("graph",default = 'all')
    month = json.loads(request.args.get("month",default = "[8]"))
    print(month)
    print(type(month))
    collection = initialize_mongoDB(HOST,DATABASE,COLLECTION)

    query = [{"$match": {"month":{"$in":month}}},{"$project": {"year":1,"month":1,"day":1, "count": 1,"_id": 0}},
            {"$sort":{"year":1,"month":1,"day":1}}]
    results = list(collection.aggregate(query))
    '''
    if graph == 'all':
        query = {"_id":param_id}
        results = list(collection.find(query))
    else:
        query = [{"$match": {"_id":param_id}}, {"$project": {"_id" : "$_id", graph: 1}}]
        results = list(collection.aggregate(query))
    '''
    print(results)
    return json.dumps(list(results))



@api_cdm.route('/streamlit', methods=["POST"])
def streamlit_redirect():
    payload =   {
                "link": "http://127.0.0.1:8501"
                }
    code = 302
    response = make_response(jsonify(payload), code)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.status_code = 302

    return response


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

    return jsonify(risultato)




@api_cdm.route('/map-data',methods=['GET'])
def mapdata():
    result =  [
        {
            "id":1,
            "description":"Nice City",
            "name":"Torino",
            "lat":45.0703,
            "long":7.6869,
            "total_trips":39082
        },
        {
            "id":2,
            "description":"Nice City",
            "name":"Milano",
            "lat":45.4642,
            "long":9.1900,
            "total_trips":647168
        },
        {
            "id":3,
            "description":"Nice City",
            "name":"New York City",
            "lat":40.7128,
            "long":-74.0060,
            "total_trips":647168
        }
    ]
   
    return jsonify(result)