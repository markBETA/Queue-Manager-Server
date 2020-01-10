"""
This module contains the socketio namespaces base class.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask_socketio import Namespace as _Namespace


class Namespace(_Namespace):
    """
    This class add an internal method for logging data processing errors for the Socket.IO namespaces.
    """
    def __init__(self, *args, **kwargs):
        self.app = None
        super(Namespace, self).__init__(*args, **kwargs)

    def init_app(self, app):
        self.app = app

    def _log_event_processing_error(self, event_name, errors):
        self.app.logger.error("Error (de)serializing data of event '" + event_name + "'. Errors:")
        for error, desc in errors.items():
            self.app.logger.error("\t- " + str(error) + ": " + desc)
