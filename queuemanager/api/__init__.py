"""
This module defines the all the API routes, namespaces, and resources
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .definitions import api, api_bp
from .files import api as files_ns
from .jobs import api as jobs_ns
from .printer import api as printer_ns
from .users import api as users_ns


def init_app(app, *_args, **_kwargs):
    """ Initialize the API main object """
    # Set the API docs enabled or disabled
    api._doc = ('/doc' if app.config.get("DEBUG") > 0 else False)
    # Initialize the API object
    api.init_app(api_bp, add_specs=(app.config.get("DEBUG") > 0))
    # Add the namespaces to the API object

    api.add_namespace(files_ns, "/files")
    api.add_namespace(jobs_ns, "/jobs")
    api.add_namespace(printer_ns, "/printer")
    api.add_namespace(users_ns, '/users')

    # Register the API blueprint
    app.register_blueprint(api_bp, url_prefix='/api')

    from ..error_handlers import set_exception_handlers
    # Set the error handlers from the API object
    set_exception_handlers(api, from_api=True)
