"""
This server stores the data sent from the printers and has methods to retrieve it.
In this package has all needed modules for the mentioned server.
"""

__author__ = "Eloi Pardo"
__credits__ = ["Eloi Pardo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Eloi Pardo"
__email__ = "epardo@fundaciocim.org"
__status__ = "Development"

import os
from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

from . import events


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    # ensure the folder to save the gcodes exists
    os.makedirs(app.config.get('GCODE_STORAGE_PATH'), exist_ok=True)

    # register the database commands
    from . import db_models
    db_models.init_app(app)

    socketio.init_app(app)

    # apply the blueprints to the app
    with app.app_context():
        from queuemanager.api_resources import api_bp
        app.register_blueprint(api_bp)

    return app

