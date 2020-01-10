"""
This module defines the all the API resources for the printer namespace.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .definitions import api
from .models import (
    printer_model, printer_extruder_type_model, printer_material_model, printer_current_job_model,
    printer_extruder_model, printer_model_model, printer_state_model
)
from .resources import (
    Printer,  PrinterMaterials, PrinterExtruderTypes
)
