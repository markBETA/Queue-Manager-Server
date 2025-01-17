"""
This module defines the all the API models of the files namespace.
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
from ..definitions import TimeToSecondsField

###########################
# FILE MODELS DECLARATION #
###########################

file_model = api.model('File', {
    'id': fields.Integer,
    'name': fields.String,
    'created_at': fields.DateTime(attribute="createdAt"),
    'estimated_printing_time': TimeToSecondsField(attribute="estimatedPrintingTime"),
    'estimated_needed_material': fields.Float(attribute="estimatedNeededMaterial")
})
