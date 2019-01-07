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
from flask_restplus import Api

from queuemanager.resources.Job import api as jobs_namespace
from queuemanager.resources.Queue import api as queues_namespace

# GLOBAL VARIABLES
api_bp = Blueprint('queuemanagerapi', __name__, url_prefix='/queuemanagerapi')
api = Api(api_bp, doc="/doc", title="Queue Manager Server", description="Server to manage a queue of jobs to be printed")
api.add_namespace(jobs_namespace)
api.add_namespace(queues_namespace)
