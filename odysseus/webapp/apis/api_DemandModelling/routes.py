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
    """
    The demand modelling module can be run only on data that has been normalized 
    """
    level = 'norm'#request.args.get("level", default = 'norm')
    filename = os.path.join(
	    os.path.abspath(os.curdir),
        "odysseus","webapp","apis","api_cityDataManager",f"{level}-data.json"
        )
    with open(filename, 'r') as f:
            summary = json.load(f)
    return jsonify(summary)

@api_dm.route('/existing_models',methods=['GET'])
def existing_models():
    """
    the module cannot be run if it's already present a model for that city, independent from time period
    """
    ROOT_DIR = os.path.abspath(os.curdir)
    demand_model_path = os.path.join(
        ROOT_DIR,
        "odysseus",
        "demand_modelling",
        "demand_models",
    )
    avalaible_cities = {}
    for f in os.scandir(demand_model_path):
        if f.is_dir():
            avalaible_cities[f.path.split("/")[-1]]=[]
            for models in os.scandir(os.path.join(demand_model_path,f)):
                if models.is_dir() and os.path.exists(os.path.join(models.path,"city_obj.pickle")):
                    avalaible_cities[f.path.split("/")[-1]].append(os.path.basename(os.path.normpath(models.path)))
    payload =   avalaible_cities
    code = 200
    response = make_response(jsonify(payload), code)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.status_code = code
    return response

@api_dm.route('/run_dm',methods=['POST'])
def run_dm():
    try:
        data = request.get_json(force=True)
        print("data received from the form", data)


        # {'values': 
        #     {'city': 'Torino', 
        #     'datasource': 'big_data_db', 
        #     'datasources': [{'value': 'big_data_db', 'label': 'big_data_db'}], 
        #     'year': 2017, 
        #     'allYears': [{'value': '2016', 'label': '2016'}, {'value': '2017', 'label': '2017'}, {'value': '2018', 'label': '2018'}], 
        #     'yearTest': 2017, 
        #     'allYearsTest': [{'value': '2017', 'label': '2017'}, {'value': '2018', 'label': '2018'}], 
        #     'month': 4, 
        #     'allMonths': [{'value': '4', 'label': '4'}, {'value': '5', 'label': '5'}, {'value': '7', 'label': '7'}, {'value': '8', 'label': '8'}, {'value': '9', 'label': '9'}, {'value': '10', 'label': '10'}, {'value': '11', 'label': '11'}, {'value': '12', 'label': '12'}], 
        #     'endMonth': 5, 
        #     'allEndMonths': [{'value': '5', 'label': '5'}, {'value': '7', 'label': '7'}, {'value': '8', 'label': '8'}, {'value': '9', 'label': '9'}, {'value': '10', 'label': '10'}, {'value': '11', 'label': '11'}, {'value': '12', 'label': '12'}], 
        #     'monthTest': 5, 
        #     'allMonthsTest': [{'value': '5', 'label': '5'}, {'value': '7', 'label': '7'}, {'value': '8', 'label': '8'}, {'value': '9', 'label': '9'}, {'value': '10', 'label': '10'}, {'value': '11', 'label': '11'}, {'value': '12', 'label': '12'}], 
        #     'endMonthTest': 7, 
        #     'allEndMonthsTest': [{'value': '7', 'label': '7'}, {'value': '8', 'label': '8'}, {'value': '9', 'label': '9'}, {'value': '10', 'label': '10'}, {'value': '11', 'label': '11'}, {'value': '12', 'label': '12'}], 
        #     'demandModelType': 'Kde Poisson', 
        #     'bin_side_lenght': '500', 
        #     'k_zones_factor': '1', 
        #     'kde_bandwidth': '0.5'}
        # }
        

        # The values needed to run the Demand Modelling are:
        # city, datasource, year, month, endMonth, sim_technique, bin_side_lenght, k_zones_factor, kde_bandwidth,save folder


        form_inputs = data["values"]
        
        dict_for_dm_modelling = {
            "cities":[form_inputs["city"]],
            "data_source_ids":[form_inputs["datasource"]],
            "sim_techniques":[form_inputs["demandModelType"]],
            "bin_side_lengths":[str(form_inputs["bin_side_lenght"])],
            "zones_factors":[str(form_inputs["k_zones_factor"])],
            "kde_bandwidths":[str(form_inputs["kde_bandwidth"])],
            "train_range":[str(form_inputs["year"]), str(form_inputs["month"]), str(form_inputs["year"]), str(form_inputs["endMonth"])],
            "test_range":[str(form_inputs["yearTest"]), str(form_inputs["monthTest"]), str(form_inputs["yearTest"]), str(form_inputs["endMonthTest"])],
            "save_folder":[form_inputs["save_folder"]]
        }

        print("STARTING THE DEMAND MODELLING MODULE WITH CONFIG",dict_for_dm_modelling )
        dm = DemandModelling(dict_for_dm_modelling)
        print("Start Run")
        status = dm.run()

        
        payload =  {
                "link": "http://127.0.0.1:8501",
                }
        code = 302
        response = make_response(jsonify(payload), code)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.status_code = code
        # if status["status"] == "complete":
            # payload =  status.update({
            #     "link": "http://127.0.0.1:8501",
            #     })
            # code = 302
            # response = make_response(jsonify(payload), code)
            # response.headers['Access-Control-Allow-Origin'] = '*'
            # response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            # response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
            # response.status_code = code
        
        # testing form submission
        # payload =   {
        #         "link": "http://127.0.0.1:8501"
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


