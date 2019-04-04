"""
This module defines the all the api resources for the printer namespace
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .definitions import api
from .models import (
    printer_model_model, printer_state_model, printer_material_model,
    printer_extruder_type_model, printer_extruder_model, printer_model
)
