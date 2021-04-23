from flask import Blueprint, render_template, redirect, url_for, request,make_response,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from odysseus.webapp.apis.api_auth.model.user import User,init_db
api_auth = Blueprint('api_auth', __name__)
CORS(api_auth)

@api_auth.route('/login', methods=['POST'])
def login_post():
    data = request.get_json(force=True)
    form_inputs = data["formData"]
    email = form_inputs['email']
    password = form_inputs['password']
    remember = True if form_inputs['remember'] else False
    print(email)
    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password_hash, password):
        #flash('Please check your login details and try again.')
        code = 403
        payload =   {
                "message":"Please check your login details and try again.",
                "link": "http://127.0.0.1:3000",
                "code": code
                }
        response = make_response(jsonify(payload), code)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.status_code = code
        return response # if the user doesn't exist or password is wrong, reload the page
    code = 200
    payload =   {
                "message":"Welcome on Odysseus.",
                "link": "http://127.0.0.1:3000",
                "code": code
                }
    code = 200
    response = make_response(jsonify(payload), code)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.status_code = code
    # if the above check passes, then we know the user has the right credentials
    return response

@api_auth.route('/register',methods=['POST'])
def register():
    data = request.get_json(force=True)
    form_inputs = data["formData"]
    email = form_inputs['email']
    password = form_inputs['password']
    user = User(
        email=email, 
        password=password)
    try:
        user.register()
        code = 200
        payload =   {
                    "message":"User successfully added",
                    "link": "http://127.0.0.1:3000",
                    "code": code
                    }
        response = make_response(jsonify(payload), code)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.status_code = code
        return response
    except Exception as e:
        code = 500
        payload =   {
                    "message":f"Something went wrong! Error {e}",
                    "link": "http://127.0.0.1:3000",
                    "code": code
                    }
        response = make_response(jsonify(payload), code)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.status_code = code
        return response

#create all db tables
@api_auth.before_app_first_request
def create_tables():
    from odysseus.webapp.apis.api_auth.model.user import User,init_db
    init_db()