# importing the flask class
from flask import Flask
from flask_cors import CORS
import os
from odysseus.webapp.apis.api_auth.config import Config
from odysseus.webapp.database_handler import DatabaseHandler
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import json

app = Flask(__name__)  # as an instance
app.config.from_object(Config)
db = SQLAlchemy(app)
db.app = app

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(email):
    from odysseus.webapp.apis.api_auth.model import User
    return User.query.filter_by(email=email).first()

# Build the database:
# This will create the database file using SQLAlchemy
#db.create_all()

def create_app():
    with open(os.path.join(os.path.abspath(os.curdir),"odysseus/webapp/settings.json"),"r") as f:
        dbdata=json.load(f)["mongodb"]
        dbdata["password"]=os.environ["MONGODB_PASSWORD"]

    app.config["HOST"] = dbdata["connection_type"]+dbdata["user"]+":"+dbdata["password"]+"@"+dbdata["endpoint"] #'mongodb://localhost:27017/'
    app.config["DATABASE"] = dbdata['database']

    from odysseus.webapp.apis.api_cityDataManager.routes import api_cdm
    app.register_blueprint(api_cdm, url_prefix='/api_cdm')

    from odysseus.webapp.apis.api_DemandModelling.routes import api_dm
    app.register_blueprint(api_dm, url_prefix='/api_dm')

    from odysseus.webapp.apis.api_SupplyModelling.routes import api_sm
    app.register_blueprint(api_sm, url_prefix='/api_sm')

    from odysseus.webapp.apis.api_simulator.routes import api_sim
    app.register_blueprint(api_sim, url_prefix='/api_sim')

    from odysseus.webapp.apis.api_test_bokeh.routes import api_bokeh
    app.register_blueprint(api_bokeh, url_prefix='/api_bokeh')

    from odysseus.webapp.apis.api_auth.routes import api_auth
    app.register_blueprint(api_auth, url_prefix='/api_auth')
    
    return app
