from flask import Blueprint, jsonify, request

api_cdm = Blueprint('api_cdm', __name__)

@api_cdm.route('/config',methods=['POST'])
def config():
    data = request.get_json()
    print(data)    
    return jsonify({'hi':1})

