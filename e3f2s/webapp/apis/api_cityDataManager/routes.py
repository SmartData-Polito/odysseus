from flask import Blueprint, jsonify, request
from e3f2s.webapp.emulate_module.city_data_manager import CityDataManager

api_cdm = Blueprint('api_cdm', __name__)

@api_cdm.route('/config',methods=['POST'])
def config():
    print("Received post")
    data = request.get_json()
    print(data)
    f = open("sim_general_conf.py","w")
    f.write("sim_general_conf_grid = "+ str(data))
    return jsonify({'config':1})

@api_cdm.route('/run',methods=['GET'])
def run():
    print("Start simulation")
    cdm = CityDataManager()
    cdm.run()
    return jsonify({'Done':1})


