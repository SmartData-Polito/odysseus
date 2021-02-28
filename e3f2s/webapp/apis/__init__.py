# importing the flask class
from flask import Flask


def create_app():
    app = Flask(__name__)  # as an instance

    from e3f2s.webapp.apis.api_cityDataManager.routes import api_cdm
    app.register_blueprint(api_cdm,host='0.0.0.0', url_prefix='/api_cdm')

    return app
