"""
This module defines the all the api models of the jobs namespace
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .definitions import api
from ..printer.models import printer_material_model, printer_extruder_type_model
from ..files.models import file_model
from ..users.models import user_model
from flask_restplus import fields


##########################
# JOB MODELS DECLARATION #
##########################

job_state_model = api.model('JobState', {
    'id': fields.Integer,
    'string': fields.String(attribute="stateString")
})

job_allowed_material_model = api.model('JobAllowed', {
    'material': fields.Nested(printer_material_model),
    'extruder_index': fields.Integer(attribute="extruderIndex")
})

job_allowed_extruder_model = api.model('JobAllowed', {
    'type': fields.Nested(printer_extruder_type_model),
    'extruder_index': fields.Integer(attribute="extruderIndex")
})

job_model = api.model('Job', {
    'id': fields.Integer,
    'name': fields.String(required=True),
    'can_be_printed': fields.Boolean(attribute="canBePrinted"),
    'created_at': fields.DateTime(attribute="createdAt"),
    'updated_at': fields.DateTime(attribute="updatedAt"),
    'state': fields.Nested(job_state_model),
    'file': fields.Nested(file_model),
    'user': fields.Nested(user_model),
    'allowed_materials': fields.Nested(job_allowed_material_model, as_list=True),
    'allowed_extruder_types': fields.Nested(job_allowed_extruder_model, as_list=True)
})
