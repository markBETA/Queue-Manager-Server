"""
This module defines all the custom fields used by the socket.io data schemas
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.2"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from datetime import timedelta

from marshmallow import fields

from ...database import db_mgr


###################################
# PRINTER NAMESPACE CUSTOM FIELDS #
###################################

class PrinterStateField(fields.String):
    """ Custom field for deserialize the printer state field """
    def _deserialize(self, value, attr, data):
        if value is None:
            return None
        elif value not in db_mgr.printer_state_ids.keys():
            value = "Unknown"
        return value


class PrinterMaterialField(fields.String):
    """ Custom field for deserialize the printer material """
    def _deserialize(self, value, attr, data):
        if value is None:
            return None
        elif isinstance(value, str):
            materials = db_mgr.get_printer_materials(type=value)
            if materials:
                return materials[0]
            else:
                return None
        else:
            self.fail('invalid')


class PrinterExtruderTypeField(fields.Float):
    """ Custom field for deserialize the printer extruder type """
    def _deserialize(self, value, attr, data):
        if value is None:
            return None
        elif isinstance(value, float):
            extruder_types = db_mgr.get_printer_extruder_types(nozzleDiameter=value)

            if extruder_types:
                return extruder_types[0]
            else:
                return None
        else:
            self.fail('invalid')


class PrintingTimeField(fields.Float):
    """ Custom field for serialize and deserialize the printing time """
    def _serialize(self, value, attr, data):
        if value is None:
            return None
        elif isinstance(value, timedelta):
            return value.total_seconds()
        else:
            self.fail('invalid')

    def _deserialize(self, value, attr, data):
        if value is None:
            return None
        elif isinstance(value, float) or isinstance(value, int):
            return timedelta(seconds=value)
        else:
            self.fail('invalid')


class EstimatedSecondsLeft(PrintingTimeField):
    """ Custom field for deserialize the estimated printing time left """
    pass


#########################
# PRINTER CUSTOM FIELDS #
#########################

class TotalPrintingTime(PrintingTimeField):
    """ Custom field for serialize and deserialize the total printing time """
    pass
