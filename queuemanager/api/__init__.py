"""
This module defines the all the API routes, namespaces, and resources
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .definitions import api, api_bp
from .files import api as files_ns
from .jobs import api as jobs_ns
from .jwt_manager import jwt_manager
from .printer import api as printer_ns


def init_app(app):
    """ Initialize the API main object """
    # Initialize the JWT manager object
    jwt_manager.init_app(app)

    # Set the API docs enabled or disabled
    api._doc = ('/doc' if app.config.get("DEBUG") > 0 else False)
    # Initialize the API object
    api.init_app(api_bp, add_specs=(app.config.get("DEBUG") > 0))
    # Add the namespaces to the API object

    api.add_namespace(files_ns, "/files")
    api.add_namespace(jobs_ns, "/jobs")
    api.add_namespace(printer_ns, "/printer")

    # Register the API blueprint
    app.register_blueprint(api_bp, url_prefix='/api')

    from ..error_handlers import set_exception_handlers
    # Set the error handlers from the API object
    jwt_manager.set_error_handler_callbacks(api)
    set_exception_handlers(api, from_api=True)
