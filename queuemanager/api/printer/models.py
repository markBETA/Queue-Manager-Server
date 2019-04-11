"""
This module defines the all the api models of the printer namespace
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask_restplus import fields

from .definitions import api
from ..definitions import TimeToSecondsField

##############################
# PRINTER MODELS DECLARATION #
##############################

printer_model_model = api.model('PrinterModel', {
    'id': fields.Integer,
    'name': fields.String,
    'width': fields.Float,
    'depth': fields.Float,
    'height': fields.Float
})

printer_state_model = api.model('PrinterState', {
    'id': fields.Integer,
    'string': fields.String(attribute="stateString"),
    'is_operational_state': fields.Boolean(attribute="isOperationalState")
})

printer_extruder_type_model = api.model('PrinterExtruderType', {
    'id': fields.Integer,
    'brand': fields.String,
    'nozzle_diameter': fields.Float(attribute="nozzleDiameter")
})

printer_material_model = api.model('PrinterMaterial', {
    'id': fields.Integer,
    'type': fields.String,
    'color': fields.String,
    'brand': fields.String,
    'guid': fields.String(attribute="GUID"),
    'print_temp': fields.Float(attribute="printTemp"),
    'bed_temp': fields.Float(attribute="bedTemp")
})

printer_extruder_model = api.model('PrinterExtruder', {
    'type': fields.Nested(printer_extruder_type_model),
    'material': fields.Nested(printer_material_model),
    'index': fields.Integer
})

printer_model = api.model('Printer', {
    'id': fields.Integer,
    'name': fields.String,
    'model': fields.Nested(printer_model_model),
    'state': fields.Nested(printer_state_model),
    'extruders': fields.Nested(printer_extruder_model, as_list=True),
    'serial_number': fields.String(attribute="serialNumber"),
    'ip_address': fields.String(attribute="ipAddress"),
    'registered_at': fields.DateTime(attribute="registeredAt"),
    'total_success_prints': fields.Integer(attribute="totalSuccessPrints"),
    'total_failed_prints': fields.Integer(attribute="totalFailedPrints"),
    'total_printing_time': TimeToSecondsField(attribute="totalPrintingTime"),
})
