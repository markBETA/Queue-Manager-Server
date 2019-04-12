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

from .printer import PrinterSchema
from .printer_namespace import (
    OnPrinterTemperaturesUpdatedSchema, OnJobProgressUpdatedSchema,
)


##################
# NESTED SCHEMAS #
##################

class JobInfoSchema(Schema):
    """ Schema of the basic job information send to the client """
    id = fields.Integer(required=True)
    name = fields.String(required=True)


############################
# NAMESPACE EVENTS SCHEMAS #
############################

class EmitJobAnalyzeDoneSchema(JobInfoSchema):
    """ Schema of the 'job_analyze_done' event emitted by the server """
    pass


class EmitJobAnalyzeErrorSchema(Schema):
    """ Schema of the 'job_analyze_error' event emitted by the server """
    job = fields.Nested(JobInfoSchema, required=True, allow_none=True)
    message = fields.String(required=True)
    additional_info = fields.Dict(allow_none=True)


class EmitJobEnqueueDoneSchema(JobInfoSchema):
    """ Schema of the 'job_enqueue_done' event emitted by the server """
    pass


class EmitJobEnqueueErrorSchema(Schema):
    """ Schema of the 'job_enqueue_error' event emitted by the server """
    job = fields.Nested(JobInfoSchema, required=True, allow_none=True)
    message = fields.String(required=True)
    additional_info = fields.Dict(allow_none=True)


class EmitPrinterDataUpdatedSchema(PrinterSchema):
    """ Schema of the 'printer_data_updated' event emitted by the server """
    pass


class EmitPrinterTemperaturesUpdatedSchema(OnPrinterTemperaturesUpdatedSchema):
    """ Schema of the 'printer_temperatures_updated' event emitted by the server """
    pass


class EmitJobProgressUpdatedSchema(OnJobProgressUpdatedSchema):
    """ Schema of the 'job_progress_updated' event emitted by the server """
    pass


class EmitJobStartedSchema(JobInfoSchema):
    """ Schema of the 'job_started' event emitted by the server """
    pass


class EmitJobDoneSchema(JobInfoSchema):
    """ Schema of the 'job_done' event emitted by the server """
    pass


class OnAnalyzeJob(Schema):
    """ Schema of the 'analyze_job' event that the server is listening for """
    job_id = fields.Integer(required=True)


class OnEnqueueJob(Schema):
    """ Schema of the 'enqueue_job' event that the server is listening for """
    job_id = fields.Integer(required=True)
