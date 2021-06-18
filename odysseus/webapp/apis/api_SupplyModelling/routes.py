from flask import Blueprint, jsonify, request, make_response,current_app
from odysseus.webapp.emulate_module.supply_modelling import SupplyModelling
from odysseus.webapp.apis.api_cityDataManager.utils import *
import pymongo as pm
import json
import os
from datetime import datetime
import random
import pandas as pd
random.seed(42)
from flask_cors import CORS
api_sm = Blueprint('api_sm', __name__)
CORS(api_sm)

@api_sm.route('/available_data',methods=['GET'])
def available_data():
    """
    The supply modelling module can be run only on data that has been normalized 
    """
    level = 'norm'#request.args.get("level", default = 'norm')
    filename = os.path.join(
	    os.path.abspath(os.curdir),
        "odysseus","webapp","apis","api_cityDataManager",f"{level}-data.json"
        )
    with open(filename, 'r') as f:
            summary = json.load(f)
    return jsonify(summary)

@api_sm.route('/existing_models',methods=['GET'])
def existing_models():
    """
    the module cannot be run if it's already present a model for that city, independent from time period
    """
    ROOT_DIR = os.path.abspath(os.curdir)
    supply_model_path = os.path.join(
        ROOT_DIR,
        "odysseus",
        "supply_modelling",
        "supply_models",
    )
    avalaible_cities = {}
    for f in os.scandir(supply_model_path):
        if f.is_dir():
            avalaible_cities[f.path.split("/")[-1]]=[]
            for models in os.scandir(os.path.join(supply_model_path,f)):
                if models.is_dir() and os.path.exists(os.path.join(models.path,"supply_model.pickle")):
                    avalaible_cities[f.path.split("/")[-1]].append(os.path.basename(os.path.normpath(models.path)))
    payload =   avalaible_cities
    code = 200
    response = make_response(jsonify(payload), code)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.status_code = code
    return response

@api_sm.route('/run_sm',methods=['POST'])
def run_sm():
    collection_name = "demand_models_config"  
    try:
        dbhandler=DatabaseHandler(host=current_app.config["HOST"],database=current_app.config["DATABASE"])
        data = request.get_json(force=True)
        print("data received from the form", data)


        # {'values': 
        #     {
        #         "cities":["Amsterdam"],
                # "data_source_ids":["big_data_db"],
                # "num_vehicles":["500"],
                # "tot_n_charging_poles":["100"],
                # "n_charging_zones":["10"],
                # "year":["2017"],
                # "distributed_cps":"True",
                # "cps_placement_policy":"num_parkings",
                # "n_relocation_workers":1,
                # "folder_name":"",
                # "recover_supply_model":""}
        # }
        
        form_inputs = data["values"]
        
        dict_for_sm_modelling = {
            "cities":[form_inputs["city"]],
            "data_source_ids":[form_inputs["datasource"]],
            "num_vehicles":form_inputs["num_vehicles"],
            # "tot_n_charging_poles":form_inputs["tot_n_charging_poles"],
            # "year":form_inputs["year"],
            # "n_charging_zones":form_inputs["n_charging_zones"],
            "distributed_cps":form_inputs["distributed_cps"],
            "cps_placement_policy":form_inputs["cps_placement_policy"],
            #"n_relocation_workers":form_inputs["n_relocation_workers"],
            "folder_name":[form_inputs["save_folder"]],
            "recover_supply_model":form_inputs["recover_supply_model"]
        }

        print("STARTING THE DEMAND MODELLING MODULE WITH CONFIG",dict_for_sm_modelling )
        dm = SupplyModelling(dict_for_sm_modelling)
        print("Start Run")
        status = dm.run()

        dbhandler.upload(dict_for_sm_modelling,collection_name=collection_name)
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
        print("Something went wrong")
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

@api_sm.route('/retrieve_config',methods=['GET'])
def retrieve_sm_config():
    folder_name=request.args.get("graph",default = 'default_supply_model')
    dbhandler=DatabaseHandler(host=current_app.config["HOST"],database=current_app.config["DATABASE"])
    res = dbhandler.query({"folder_name":folder_name})
    return jsonify(res)