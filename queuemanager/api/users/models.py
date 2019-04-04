"""
This module defines the all the api models of the files namespace
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .definitions import api
from flask_restplus import fields


###########################
# USER MODELS DECLARATION #
###########################

user_model = api.model('User', {
    'id': fields.Integer,
    'username': fields.String,
    'is_admin': fields.Boolean(attribute="isAdmin"),
    'registered_on': fields.DateTime(attribute="registeredOn")
})
