"""
This module defines all schemas used by the events emitted and received by the printer namespace
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from marshmallow import Schema, fields

from .common_schemas import (
    PrinterTemperaturesUpdatedSchema, CurrentJobInfoSchema
)
from .custom_fields import (
    PrinterStateField, PrinterMaterialField, PrinterExtruderTypeField, PrintingTimeField, EstimatedSecondsLeft
)


##################
# NESTED SCHEMAS #
##################

class ExtrudersInfoSchema(Schema):
    """ Schema of the extruders information send by the printer """
    material_type = PrinterMaterialField(attribute="material", allow_none=True, required=True)
    extruder_nozzle_diameter = PrinterExtruderTypeField(attribute="extruder_type", allow_none=True, required=True)
    index = fields.Integer(required=True)


class FeedbackDataSchema(Schema):
    """ Schema of the extruders information send by the printer """
    success = fields.Boolean(required=True)
    max_priority = fields.Boolean(allow_none=True, required=True)
    printing_sec = PrintingTimeField(required=True, attribute="printing_time")


class ExtruderTempSchema(Schema):
    """ Schema of the extruders temperature send by the printer """
    temp_value = fields.Float(required=True)
    index = fields.Integer(required=True)


############################
# NAMESPACE EVENTS SCHEMAS #
############################

class EmitPrintJobSchema(Schema):
    """ Schema of the 'print_job' event emitted by the server """
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    file_id = fields.Integer(attribute="file.id", required=True)


class EmitJobRecoveredSchema(Schema):
    """ Schema of the 'job_recovered' event emitted by the server """
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    started_at = fields.DateTime(required=True, attribute='startedAt')
    interrupted = fields.Boolean(required=True)


class OnInitialDataSchema(Schema):
    """ Schema of the 'initial_data' event that the server is listening for """
    state = PrinterStateField(required=True)
    extruders_info = fields.Nested(ExtrudersInfoSchema, many=True, required=True)


class OnStateUpdatedSchema(Schema):
    """ Schema of the 'state_updated' event that the server is listening for """
    state = PrinterStateField(required=True)


class OnExtrudersUpdatedSchema(Schema):
    """ Schema of the 'extruders_updated' event that the server is listening for """
    extruders_info = fields.Nested(ExtrudersInfoSchema, many=True, required=True)


class OnPrintStartedSchema(Schema):
    """ Schema of the 'print_started' event that the server is listening for """
    job_id = fields.Integer(required=True)


class OnPrintFinishedSchema(Schema):
    """ Schema of the 'print_finished' event that the server is listening for """
    job_id = fields.Integer(required=True)
    cancelled = fields.Boolean(required=True)


class OnPrintFeedbackSchema(Schema):
    """ Schema of the 'print_finished' event that the server is listening for """
    job_id = fields.Integer(required=True)
    feedback_data = fields.Nested(FeedbackDataSchema, required=True)


class OnPrinterTemperaturesUpdatedSchema(PrinterTemperaturesUpdatedSchema):
    """ Schema of the 'printer_temperatures_updated' event that the server is listening for """
    pass


class OnJobProgressUpdatedSchema(CurrentJobInfoSchema):
    """ Schema of the 'printer_temperatures_updated' event that the server is listening for """
    estimated_seconds_left = EstimatedSecondsLeft(attribute="estimated_time_left", allow_none=True)
