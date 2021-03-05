# importing the flask class
from flask import Flask


def create_app():
    app = Flask(__name__)  # as an instance

    from e3f2s.webapp.apis.api_cityDataManager.routes import api_cdm
    app.register_blueprint(api_cdm,host='0.0.0.0', url_prefix='/api_cdm')

    from apis.api_simulator.routes import api_sim
    app.register_blueprint(api_sim, url_prefix='/api_sim')

    from apis.api_test_bokeh.routes import api_bokeh
    app.register_blueprint(api_bokeh, url_prefix='/api_bokeh')

    

    return app
