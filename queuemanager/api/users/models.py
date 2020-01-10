"""
This module defines the all the API models of the users namespace
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask_restplus import fields

from .definitions import api

###########################
# USER MODELS DECLARATION #
###########################

user_model = api.model('User', {
    'id': fields.Integer,
    'username': fields.String,
    'fullname': fields.String,
    'email': fields.String,
    'registered_on': fields.String(attribute="registeredOn")
})
