from flask import Blueprint, jsonify, request, make_response
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
api_dm = Blueprint('api_dm', __name__)
CORS(api_dm)


@api_dm.route('/hi',methods=['GET','POST'])
def hi():
    return jsonify({"hi":1})



@api_dm.route('/available_data',methods=['GET'])
def available_data():
    level = request.args.get("level", default = 'norm')
    filename = os.path.join(
	    os.path.abspath(os.curdir),
        "odysseus","webapp","apis","api_cityDataManager",f"{level}-data.json"
        )
    with open(filename, 'r') as f:
            summary = json.load(f)
    return jsonify(summary)



@api_dm.route('/run_dm',methods=['POST'])
def run_dm():
    try:
        data = request.get_json()
        print("data received from the form", data)


        # {'values': 
        #     {'city': 'Torino', 
        #     'datasource': 'big_data_db', 
        #     'datasources': [{'value': 'big_data_db', 'label': 'big_data_db'}], 
        #     'year': '2016', 
        #     'allYears': [{'value': '2016', 'label': '2016'}, {'value': '2017', 'label': '2017'}], 
        #     'month': '12',
        #     'allMonths': [{'value': '12', 'label': '12'}],
        #     'endMonth': '12',
        #     'sim_technique': 'EventG', 
        #     'bin_side_lenght': '100',
        #     'k_zones_factor': '1', 
        #     'kde_bandwidth': ''}
        # }
        # form_inputs = data["formData"]
        # cities = []
        # years = []
        # months = []
        # data_source_ids = []
        # cities.append(form_inputs["cities"])
        # years.append(form_inputs["years"])
        # months.append(form_inputs["months"])
        # data_source_ids.append(form_inputs["data_source_ids"])

        # print("EXTRACTED DATA",cities,years,months,data_source_ids)

     
        # payload =   {
        #         "link": "http://127.0.0.1:8501"
        #         }
        # code = 302
        # response = make_response(jsonify(payload), code)
        # response.headers['Access-Control-Allow-Origin'] = '*'
        # response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        # response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        # response.status_code = 302
        
        # testing form submission
        payload =   {
                "link": "http://127.0.0.1:3000"
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


