from flask import Blueprint, jsonify, request
from e3f2s.webapp.emulate_module.city_data_manager import CityDataManager

api_cdm = Blueprint('api_cdm', __name__)

@api_cdm.route('/config',methods=['POST'])
def config():
    data = request.get_json()
    print(data)
    return jsonify({'config':1})

@api_cdm.route('/run',methods=['GET','POST'])
def run():
    data = request.get_json()
    print(data)
    # ok ho finito come return, via libera per le possibili get dei risultati
    return jsonify({'run':1})


# @api_cdm.route('/run',methods=['GET'])
# def run():
#     cdm = CityDataManager()
#     cdm.run()
#     return jsonify({'Done':1})
