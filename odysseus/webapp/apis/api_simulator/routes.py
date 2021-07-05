from flask import Blueprint, jsonify, request, make_response,current_app
from odysseus.webapp.emulate_module.simulatorNew import Simulator
from odysseus.webapp.apis.api_cityDataManager.utils import *
import pymongo as pm
import json
import os
from datetime import datetime
import random
import pandas as pd
random.seed(42)
from flask_cors import CORS
api_sim = Blueprint('api_sim', __name__)

@api_sim.route('/config',methods=['POST'])
def config():
    data = request.get_json()
    print(data)
    return jsonify({'config':1})

@api_sim.route('/run',methods=['GET','POST'])
def run():
    try:
        data = request.get_json()
        print(data)
        # {'values': {'city': 'Torino', 
        # 'demModelsForCity': [{'value': 'brendan_1', 'label': 'brendan_1'}, {'value': 'brendan_3', 'label': 'brendan_3'}], 
        # 'supModelsForCity': [{'value': 'brendan_1', 'label': 'brendan_1'}, {'value': 'kiutfd', 'label': 'kiutfd'}, {'value': 'adfasdkiutfd', 'label': 'adfasdkiutfd'}], 
        # 'demandModelName': 'brendan_1',
        # 'supplyModelName': 'adfasdkiutfd'}}
        form_inputs = data["values"]
        dict_for_simulator = {
            "city":form_inputs["city"],
            "demandModelName":form_inputs["demandModelName"],
            "supplyModelName":form_inputs["supplyModelName"]
        }
        print("STARTING THE SIMULATOR MODULE WITH CONFIG\n", dict_for_simulator )
        sim = Simulator(dict_for_simulator)
        print("Start Run\n")
        status = sim.run()


        payload =  {
                    "link": "http://127.0.0.1:8501",
                    }
        code = 302
        response = make_response(jsonify(payload), code)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.status_code = code
                
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

    

