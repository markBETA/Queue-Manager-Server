"""
This file implements the way to run the server from a WSGI server with only the application API service enabled.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from queuemanager import create_app


enabled_modules = {
    "flask-cors",
    "error-handlers",
    "app-database",
    "file-storage",
    "api",
    "socketio-ext",
    "identity-mgr"
}

app = create_app(__name__, init_db_manager_values=True, enabled_modules=enabled_modules)