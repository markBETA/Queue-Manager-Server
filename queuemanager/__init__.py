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


def create_app(name=__name__, override_config=None, init_db_manager_values=False, enabled_modules="all"):
    """Create and configure an instance of the Flask application."""
    import os

    if enabled_modules == "all":
        enabled_modules = {
            "flask-cors",
            "error-handlers",
            "app-database",
            "file-storage",
            "blacklist-manager",
            "socketio",
            "api"
        }

    from flask import Flask
    app = Flask(name, instance_relative_config=True)

    if "flask-cors" in enabled_modules:
        from flask_cors import CORS
        CORS(app)

    if override_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
        # Ensure the folder to save the GCODEs exists
        if "file-storage" in enabled_modules:
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

    # Init file manager
    if "file-storage" in enabled_modules:
        from .file_storage import file_mgr
        file_mgr.init_app(app, create_upload_dir=override_config is None)

    # Init the blacklist manager
    if "blacklist-manager" in enabled_modules:
        from .blacklist_manager import jwt_blacklist_manager
        jwt_blacklist_manager.init_app(app)

    # Set the exception handlers
    if "error-handlers" in enabled_modules:
        from .error_handlers import set_exception_handlers
        set_exception_handlers(app)

    with app.app_context():
        # Register the app_database commands
        if "app-database" in enabled_modules:
            from .database import init_app as db_init_app
            db_init_app(app)

        # Init the app_database manager
        if init_db_manager_values and "app-database" in enabled_modules:
            from .database import db_mgr
            db_mgr.init_static_values()
            db_mgr.init_printers_state()
            db_mgr.init_jobs_can_be_printed()

        # Init the socket.io interface
        if "socketio" in enabled_modules:
            from .socketio import socketio
            socketio.init_app(app, logger=(app.config.get("DEBUG") > 0))

        # Register the API blueprint
        if "api" in enabled_modules:
            from .api import init_app as api_init_app
            api_init_app(app)

    return app
