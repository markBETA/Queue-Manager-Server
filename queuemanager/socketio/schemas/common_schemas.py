"""
This module defines all schemas used by the events emitted and received by the client namespace
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from marshmallow import Schema, fields

from .custom_fields import (
    EstimatedSecondsLeft, ElapsedSeconds
)


##################
# NESTED SCHEMAS #
##################

class ExtruderTempSchema(Schema):
    """ Schema of the extruders temperature send by the printer """
    temp_value = fields.Float(required=True)
    index = fields.Integer(required=True)


##################
# COMMON SCHEMAS #
##################

class PrinterTemperaturesUpdatedSchema(Schema):
    """ Schema of the 'printer_temperatures_updated' event that the server is listening for """
    bed_temp = fields.Float(required=True)
    extruders_temp = fields.Nested(ExtruderTempSchema, many=True, required=True)


class JobProgressUpdatedSchema(Schema):
    """ Schema of the 'printer_temperatures_updated' event that the server is listening for """
    job_id = fields.Integer(required=True)
    progress = fields.Float(required=True)
    elapsed_seconds = ElapsedSeconds(attribute="elapsed_time", required=True)
    estimated_seconds_left = EstimatedSecondsLeft(attribute="estimated_time_left", required=True, allow_none=True)
