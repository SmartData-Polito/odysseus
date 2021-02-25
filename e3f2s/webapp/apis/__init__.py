# importing the flask class
from flask import Flask


def create_app():
    app = Flask(__name__)  # as an instance

    from apis.api_cityDataManager.routes import api_cdm
    app.register_blueprint(api_cdm, url_prefix='/api_cdm')

    return app
