"""
This module defines all the printer data schemas for the socket.io namespaces
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from marshmallow import Schema, fields

from .common_schemas import CurrentJobInfoSchema
from .custom_fields import TotalPrintingTime
from ...database import (
    PrinterModel, PrinterState, PrinterExtruderType, PrinterMaterial, PrinterExtruder, Printer
)


class PrinterModelSchema(Schema):
    """ Schema for the 'printer_models' table """
    __model__ = PrinterModel

    id = fields.Integer()
    name = fields.String()
    width = fields.Float()
    depth = fields.Float()
    height = fields.Float()


class PrinterStateSchema(Schema):
    """ Schema for the 'printer_states' table """
    __model__ = PrinterState

    id = fields.Integer()
    string = fields.String(attribute="stateString")
    is_operational_state = fields.Boolean(attribute="isOperationalState")


class PrinterExtruderTypeSchema(Schema):
    """ Schema for the 'printer_extruder_types' table """
    __model__ = PrinterExtruderType

    id = fields.Integer()
    brand = fields.String()
    nozzle_diameter = fields.Float(attribute="nozzleDiameter")


class PrinterMaterialSchema(Schema):
    """ Schema for the 'printer_materials' table """
    __model__ = PrinterMaterial

    id = fields.Integer()
    type = fields.String()
    color = fields.String(allow_none=True)
    brand = fields.String(allow_none=True)
    guid = fields.String(attribute="GUID", allow_none=True)
    print_temp = fields.Float(attribute="printTemp")
    bed_temp = fields.Float(attribute="bedTemp")


class PrinterExtruderSchema(Schema):
    """ Schema for the 'printer_extruders' table """
    __model__ = PrinterExtruder

    type = fields.Nested(PrinterExtruderTypeSchema, allow_none=True)
    material = fields.Nested(PrinterMaterialSchema, allow_none=True)
    index = fields.Integer(attribute="index")


class PrinterSchema(Schema):
    """ Schema for the 'printers' table """
    __model__ = Printer

    id = fields.Integer()
    name = fields.String()
    model = fields.Nested(PrinterModelSchema)
    state = fields.Nested(PrinterStateSchema)
    extruders = fields.Nested(PrinterExtruderSchema, many=True)
    serial_number = fields.String(attribute="serialNumber")
    ip_address = fields.String(attribute="ipAddress", allow_none=True)
    registered_at = fields.DateTime(attribute="registeredAt")
    total_success_prints = fields.Integer(attribute="totalSuccessPrints")
    total_failed_prints = fields.Integer(attribute="totalFailedPrints")
    total_printing_seconds = TotalPrintingTime(attribute="totalPrintingTime")
    current_job = fields.Nested(CurrentJobInfoSchema, allow_none=True)
