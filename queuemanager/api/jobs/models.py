"""
This module defines the all the API models of the jobs namespace.
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
from ..files.models import file_model
from ..printer.models import printer_material_model, printer_extruder_type_model, printer_model
from ..users.models import user_model

##########################
# JOB MODELS DECLARATION #
##########################

job_state_model = api.model('JobState', {
    'id': fields.Integer,
    'string': fields.String(attribute="stateString")
})

job_allowed_material_model = api.model('JobAllowedMaterial', {
    'material': fields.Nested(printer_material_model),
    'extruder_index': fields.Integer(attribute="extruderIndex")
})

job_allowed_extruder_model = api.model('JobAllowedExtruder', {
    'type': fields.Nested(printer_extruder_type_model),
    'extruder_index': fields.Integer(attribute="extruderIndex")
})

job_extruder_model = api.model('JobExtruder', {
    'used_extruder_type': fields.Nested(printer_extruder_type_model, skip_none=True),
    'used_material': fields.Nested(printer_material_model, skip_none=True),
    'estimated_needed_material': fields.Float(attribute="estimatedNeededMaterial"),
    'extruder_index': fields.Integer(attribute="extruderIndex")
})

job_model = api.model('Job', {
    'id': fields.Integer,
    'name': fields.String(required=True),
    'can_be_printed': fields.Boolean(attribute="canBePrinted"),
    'analyzed': fields.Boolean,
    'created_at': fields.DateTime(attribute="createdAt"),
    'started_at': fields.DateTime(attribute="startedAt"),
    'finished_at': fields.DateTime(attribute="finishedAt"),
    'retries': fields.Integer,
    'succeed': fields.Boolean,
    'state': fields.Nested(job_state_model),
    'file': fields.Nested(file_model),
    'user': fields.Nested(user_model),
    'assigned_printer': fields.Nested(printer_model, skip_none=True),
    'allowed_materials': fields.Nested(job_allowed_material_model, as_list=True, skip_none=True),
    'allowed_extruder_types': fields.Nested(job_allowed_extruder_model, as_list=True, skip_none=True),
    'extruders_data': fields.Nested(job_extruder_model, as_list=True, skip_none=True)
})

edit_job_model = api.model('EditJob', {
    'name': fields.String,
})

reorder_job_model = api.model('ReorderJob', {
    'previous_job_id': fields.Integer(required=True, min=-1)
})
