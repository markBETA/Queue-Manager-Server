"""
This server stores the data sent from the printers and has methods to retrieve it.
In this package has all needed modules for the mentioned server.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from eventlet import monkey_patch

monkey_patch()


def create_app(name=__name__, override_config=None, init_db_static_values=False):
    """Create and configure an instance of the Flask application."""
    import os

    from flask import Flask
    app = Flask(name, instance_relative_config=True)

    from flask_cors import CORS
    CORS(app)

    if override_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
        # Ensure the folder to save the GCODEs exists
        os.makedirs(app.config.get('FILE_MANAGER_UPLOAD_DIR'), exist_ok=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(override_config)

    from logging import INFO, DEBUG

    # Set the logger level
    if app.config.get("DEBUG") > 1:
        app.logger.setLevel(DEBUG)
    else:
        app.logger.setLevel(INFO)

    # Register the database commands
    from .database import init_app as db_init_app
    db_init_app(app)

    # Init file manager
    from .file_storage import file_mgr
    file_mgr.init_app(app)

    with app.app_context():
        if init_db_static_values:
            # Init the database manager
            from .database import db_mgr
            db_mgr.init_static_values()
            db_mgr.init_printers_state()
            db_mgr.init_jobs_can_be_printed()

        # Init the socket.io interface
        from .socketio import socketio
        socketio.init_app(app, logger=(app.config.get("DEBUG") > 0))

        # Register the API blueprint
        from queuemanager.api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')

    return app
