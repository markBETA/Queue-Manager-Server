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

from flask import Blueprint
from flask_restplus import Api

from .files import api as files_ns
from .jobs import api as jobs_ns
from .printer import api as printer_ns
from .users import api as users_ns

api_bp = Blueprint('api', __name__)

api = None


def init_app(app):
    """ Initialize the API main object """
    global api

    api = Api(
        title='Queue Manager API',
        version='0.1',
        description='This API manages all the data operations for the queue manager',
        doc=('/doc' if app.config.get("DEBUG") > 0 else False)
    )

    api.init_app(api_bp, add_specs=(app.config.get("DEBUG") > 0))

    api.add_namespace(files_ns, "/files")
    api.add_namespace(jobs_ns, "/jobs")
    api.add_namespace(printer_ns, "/printer")
    api.add_namespace(users_ns, "/users")

    app.register_blueprint(api_bp, url_prefix='/api')
