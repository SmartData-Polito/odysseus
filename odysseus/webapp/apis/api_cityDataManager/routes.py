from flask import Blueprint, app,current_app, jsonify, request,make_response
from odysseus.webapp.emulate_module.city_data_manager import CityDataManager
from odysseus.webapp.apis.api_cityDataManager.utils import *
from odysseus.webapp.database_handler import DatabaseHandler
import json
import os
from datetime import datetime
import random
import pandas as pd
random.seed(42)
from flask_cors import CORS
api_cdm = Blueprint('api_cdm', __name__)
CORS(api_cdm)


@api_cdm.route('/run_cdm',methods=['POST'])
def run_cdm():
    """
    Receive the configuration from the front end and run simulation
    
    {
    "values":{
        "city":"Torino",
        "datasource":"big_data_db",
        "datasources":[
            {
                "value":"big_data_db",
                "label":"big_data_db"
            }
        ],
        "year":"2018",
        "allYears":[
            {
                "value":"2016",
                "label":"2016"
            },
            {
                "value":"2017",
                "label":"2017"
            },
            {
                "value":"2018",
                "label":"2018"
            }
        ],
        "month":1,
        "allMonths":[
            {
                "value":"1",
                "label":"1"
            }
        ],
        "endMonth":1,
        "allEndMonths":[
            {
                "value":"1",
                "label":"1"
            }
        ]
    }
    }

    """
    try:
        dbhandler=DatabaseHandler(host=current_app.config["HOST"],database=current_app.config["DATABASE"])
        data = request.get_json(force=True)
        print("data received from the form", data)
        form_inputs = data["values"]
        city = []
        year = []
        months = []
        datasource = []
        if type(form_inputs["city"])==list:
            city = form_inputs["city"]
        else:
            city.append(form_inputs["city"])
        if type(form_inputs["year"])==list:
            year = form_inputs["year"]
        else:
            year.append(form_inputs["year"])
        if type(form_inputs["month"])==list:
            months = form_inputs["month"]
        else:
            if form_inputs["month"] == form_inputs["endMonth"]:
                months.append(str(form_inputs["month"]))
                    
            else:
                for i in range(form_inputs["month"], form_inputs["endMonth"]+1):
                    months.append(str(i))
                    i+=1


        if type(form_inputs["datasource"])==list:
            datasource = form_inputs["datasource"]
        else:
            datasource.append(form_inputs["datasource"])

        print("EXTRACTED DATA",city,year,months,datasource)

        cdm = CityDataManager(city,year,months,datasource,dbhandler=dbhandler)
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

@api_cdm.route('/test',methods=['GET'])
def test():
    print("Return available data per cities")
    summary = summary_available_data_per_hour(DEBUG=False)
    return jsonify(summary)


@api_cdm.route('/zones_test',methods=['GET'])
def zone_test():
    print("Return available data per cities")
    summary = summary_available_data_per_zone(DEBUG=False)
    return jsonify(summary)


@api_cdm.route('/get-cdm-data',methods=['GET'])
def get_data():
    param_id = request.args.get("id",default = 'TEST')
    graph = request.args.get("graph",default = 'all')
    city = request.args.get("city",default = "Torino")
    year = json.loads(request.args.get("year",default = "[2017]"))
    month = json.loads(request.args.get("month",default = "[8]"))
    print(city," ",year,"-",month)
    #_,collection = initialize_mongoDB(HOST,DATABASE,COLLECTION)
    dbhandler=DatabaseHandler(host=current_app.config["HOST"],database=current_app.config["DATABASE"])
    #query = [{"$match": {"city":str(city),"year":{"$in":year},"month":{"$in":month}}},{"$project": {"city":1,"year":1,"month":1,"day":1, "n_bookings": 1,"avg_duration":1,"_id": 0}},{"$sort":{"year":1,"month":1,"day":1}}]
    query = [
        {
            "$match": {"city":str(city),"year":{"$in":year},"month":{"$in":month}}
        },
        {
            "$project": {
                "city":1,
                "year":1,
                "month":1,
                "day":1,
                "n_booking": 1,
                'avg_duration':1, 
                "_id": 0}
        },
        { 
            '$unwind' : {'path': "$n_booking",'includeArrayIndex': "hour_bookings"}
        },
        { 
            '$unwind' : {'path': "$avg_duration",'includeArrayIndex': "hour_duration"}
        },
        {
            '$project': {
                "year":1,
                "month":1,
                "day":1,
                'n_booking':1, 
                'avg_duration':1, 
                'hour': "$hour_bookings",
                'compare': {'$cmp': ['$hour_bookings', '$hour_duration']}}
        },
        {
            '$match': {'compare': 0}
        },
        {
            '$project':{
                'date': { '$dateFromParts': {'year' : '$year', 'month' : '$month', 'day' : '$day', 'hour' : '$hour'}},
                'n_booking':1, 
                'avg_duration':1, 
            }
        }
        ]
    
    #results = list(collection.aggregate(query))
    results = dbhandler.query(query)
    '''
    if graph == 'all':
        query = {"_id":param_id}
        results = list(collection.find(query))
    else:
        query = [{"$match": {"_id":param_id}}, {"$project": {"_id" : "$_id", graph: 1}}]
        results = list(collection.aggregate(query))
    '''
    print(results)
    #return json.dumps(list(results))
    return json.dumps(results, default=json_util.default)


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


@api_cdm.route('/test_connectivity',methods=['GET'])
def conn_test():
    dbhandler=DatabaseHandler(host=current_app.config["HOST"],database=current_app.config["DATABASE"])
    status=dbhandler.upload({"city":1,"year":1,"month":1,"day":1},"test")
    if status is not None:
        return jsonify({"STATUS":"uploaded"})
    else:
        return jsonify({"STATUS":"Not uploaded"})

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