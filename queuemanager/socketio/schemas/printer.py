"""
This module defines the all the printer schemas for the socket.io namespaces
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from marshmallow import Schema, fields


class PrinterModelSchema(Schema):
    """ Schema for the 'printer_models' table """
    id = fields.Integer()
    name = fields.String()
    width = fields.Float()
    depth = fields.Float()
    height = fields.Float()


class PrinterStateSchema(Schema):
    """ Schema for the 'printer_states' table """
    id = fields.Integer()
    string = fields.String(attribute="stateString")
    is_operational_state = fields.Boolean(attribute="isOperationalState")


class PrinterExtruderTypeSchema(Schema):
    """ Schema for the 'printer_extruder_types' table """
    id = fields.Integer
    brand = fields.String
    nozzle_diameter = fields.Float(attribute="nozzleDiameter")


class PrinterMaterialSchema(Schema):
    """ Schema for the 'printer_materials' table """
    id = fields.Integer
    type = fields.String
    color = fields.String
    brand = fields.String
    guid = fields.String(attribute="GUID")
    print_temp = fields.Float(attribute="printTemp")
    bed_temp = fields.Float(attribute="bedTemp")


class PrinterExtruderSchema(Schema):
    type = fields.Nested(PrinterExtruderTypeSchema)
    material = fields.Nested(PrinterMaterialSchema)
    index = fields.Integer

