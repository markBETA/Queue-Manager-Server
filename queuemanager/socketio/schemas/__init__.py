"""
This module defines the all the schemas for each table defined in the socketio_printer module
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.2"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .client_namespace import (
    EmitJobAnalyzeDoneSchema, EmitJobAnalyzeErrorSchema, EmitJobEnqueueDoneSchema, EmitJobEnqueueErrorSchema,
    EmitPrinterDataUpdatedSchema, EmitPrinterTemperaturesUpdatedSchema, EmitJobProgressUpdatedSchema,
    OnAnalyzeJob, OnEnqueueJob
)
from .helpers import (
    EmitAnalyzeErrorHelper, EmitEnqueueErrorHelper, EmitPrinterTemperaturesUpdatedHelper

)
from .printer import (
    PrinterModelSchema, PrinterStateSchema, PrinterExtruderTypeSchema, PrinterMaterialSchema,
    PrinterExtruderSchema, PrinterSchema
)
from .printer_namespace import (
    EmitPrintJobSchema, EmitJobRecoveredSchema, OnInitialDataSchema, OnStateUpdatedSchema, OnExtrudersUpdatedSchema,
    OnPrintStartedSchema, OnPrintFinishedSchema, OnPrintFeedbackSchema, OnPrinterTemperaturesUpdatedSchema,
    OnJobProgressUpdatedSchema
)
