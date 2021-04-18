from flask import Blueprint, jsonify, request, make_response
from odysseus.webapp.emulate_module.demand_modelling import DemandModelling
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
        data = request.get_json(force=True)
        print("data received from the form", data)


        # {'values': 
        #     cities=["Torino", "Milano", "Vancouver"],         
        #      data_source_ids=["big_data_db"],
        #      sim_techniques=["eventG"],
        #      bin_side_lengths=["500"],
        #      zones_factors=["1"],
        #      kde_bandwidths=["1"],
        #      train_range=["2017", "10", "2017", "10"],
        #     test_range=["2017", "11", "2017", "11"],
        # }
        

        # The values needed to run the Demand Modelling are:
        # city, datasource, year, month, endMonth, sim_technique, bin_side_lenght, k_zones_factor, kde_bandwidth


        form_inputs = data["formData"]
        # cities = []
        # years = []
        # months = []
        # data_source_ids = []
        # cities.append(form_inputs["cities"])
        # years.append(form_inputs["years"])
        # months.append(form_inputs["months"])
        # data_source_ids.append(form_inputs["data_source_ids"])
        print(form_inputs)
        dm = DemandModelling(form_inputs)
        print("Start Run")
        status = dm.run()

        payload =   status.update({
                "link": "http://127.0.0.1:8501",
                })
        code = 302
        response = make_response(jsonify(payload), code)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.status_code = code
        
        # testing form submission
        # payload =   {
        #         "link": "http://127.0.0.1:3000"
        #         }
        # code = 302
        # response = make_response(jsonify(payload), code)
        # response.headers['Access-Control-Allow-Origin'] = '*'
        # response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        # response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        # response.status_code = 302
    except Exception as e:
        print(e)
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


