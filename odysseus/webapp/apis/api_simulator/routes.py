from flask import Blueprint, jsonify, request

api_sim = Blueprint('api_sim', __name__)

@api_sim.route('/config',methods=['POST'])
def config():
    data = request.get_json()
    print(data)
    return jsonify({'config':1})

@api_sim.route('/run',methods=['GET','POST'])
def run():
    data = request.get_json()
    print(data)
    # ok ho finito come return, via libera per le possibili get dei risultati
    return jsonify({'run':1})


