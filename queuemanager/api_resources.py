"""
This module implements the REST API Blueprint and defines all of its methods.
"""

__author__ = "Eloi Pardo"
__credits__ = ["Eloi Pardo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Eloi Pardo"
__email__ = "epardo@fundaciocim.org"
__status__ = "Development"

from flask import Blueprint
from flask_restful import Api
from queuemanager.resources.Print import Print, PrintList

# GLOBAL VARIABLES
api_bp = Blueprint('queuemanagerapi', __name__, url_prefix='/queuemanagerapi')
api = Api(api_bp)


# Routes definitions
api.add_resource(PrintList, '/prints')
api.add_resource(Print, '/prints/<print_id>')
