import os
from flask import Flask, Blueprint
from .routes import *


api = Blueprint('api', __name__, url_prefix='/api/v1') 

def create_app(config_overrides=None): 

    app = Flask(__name__) 

    if config_overrides: 
        app.config.update(config_overrides)

    # Load the models 
    from .routes import api_degrees, api_major, api_courses

    app.register_blueprint(api_degrees)
    app.register_blueprint(api_major)
    app.register_blueprint(api_courses)
    app.register_blueprint(api)

    return app


@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "healthy"}),200

