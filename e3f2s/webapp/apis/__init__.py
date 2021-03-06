# importing the flask class
from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)  # as an instance

    from e3f2s.webapp.apis.api_cityDataManager.routes import api_cdm
    app.register_blueprint(api_cdm, url_prefix='/api_cdm')

    from e3f2s.webapp.apis.api_simulator.routes import api_sim
    app.register_blueprint(api_sim, url_prefix='/api_sim')

    from e3f2s.webapp.apis.api_test_bokeh.routes import api_bokeh
    app.register_blueprint(api_bokeh, url_prefix='/api_bokeh')

    

    return app
