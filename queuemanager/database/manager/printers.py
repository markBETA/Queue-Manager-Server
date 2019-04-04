"""
This module contains the database manager class for the printer operations.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .base_class import DBManagerBase
from ..models import (
    PrinterModel, PrinterState, PrinterExtruderType, PrinterMaterial, PrinterExtruder,
    Printer
)
from .exceptions import (
    InvalidParameter
)
from datetime import timedelta


class DBManagerPrinterModels(DBManagerBase):
    """
    This class implements the database manager class for the printer models operations
    """
    def get_printer_models(self, **kwargs):
        # Create the query object
        query = PrinterModel.query

        # Filter by the given kwargs
        for key, value in kwargs.items():
            if hasattr(PrinterModel, key):
                if key in ("id", "name"):
                    return self.execute_query(query.filter_by(**{key: value}), use_list=False)
                else:
                    query = query.filter_by(**{key: value})
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Return all the filtered items
        return self.execute_query(query)


class DBManagerPrinterStates(DBManagerBase):
    """
    This class implements the database manager class for the printer states operations
    """
    def get_printer_states(self, **kwargs):
        # Create the query object
        query = PrinterState.query

        # Filter by the given kwargs
        for key, value in kwargs.items():
            if hasattr(PrinterState, key):
                if key in ("id", "stateString"):
                    return self.execute_query(query.filter_by(**{key: value}), use_list=False)
                else:
                    query = query.filter_by(**{key: value})
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Return all the filtered items
        return self.execute_query(query)


class DBManagerPrinterExtruderTypes(DBManagerBase):
    """
    This class implements the database manager class for the printer extruder types operations
    """
    def get_printer_extruder_types(self, **kwargs):
        # Create the query object
        query = PrinterExtruderType.query

        # Filter by the given kwargs
        for key, value in kwargs.items():
            if hasattr(PrinterExtruderType, key):
                if key == "id":
                    return self.execute_query(query.filter_by(**{key: value}), use_list=False)
                else:
                    query = query.filter_by(**{key: value})
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Return all the filtered items
        return self.execute_query(query)


class DBManagerPrinterMaterials(DBManagerBase):
    """
    This class implements the database manager class for the printer materials operations
    """
    def get_printer_materials(self, **kwargs):
        # Create the query object
        query = PrinterMaterial.query

        # Filter by the given kwargs
        for key, value in kwargs.items():
            if hasattr(PrinterMaterial, key):
                if key == "id":
                    return self.execute_query(query.filter_by(**{key: value}), use_list=False)
                else:
                    query = query.filter_by(**{key: value})
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Return all the filtered items
        return self.execute_query(query)


class DBManagerPrinterExtruders(DBManagerBase):
    """
    This class implements the database manager class for the printer extruders operations
    """
    def get_printer_extruders(self, **kwargs):
        # Create the query object
        query = PrinterExtruder.query

        # Filter by the given kwargs
        for key, value in kwargs.items():
            if hasattr(PrinterExtruder, key):
                if key == "id":
                    return self.execute_query(query.filter_by(**{key: value}), use_list=False)
                else:
                    query = query.filter_by(**{key: value})
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Return all the filtered items
        return self.execute_query(query)

    def update_printer_extruder(self, printer_extruder: PrinterExtruder, **kwargs):
        # Modify the specified job fields
        for key, value in kwargs.items():
            if hasattr(PrinterExtruder, key):
                setattr(printer_extruder, key, value)
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return printer_extruder


class DBManagerPrinters(DBManagerPrinterModels, DBManagerPrinterStates, DBManagerPrinterExtruderTypes,
                        DBManagerPrinterMaterials, DBManagerPrinterExtruders):
    """
    This class implements the database manager class for the printer extruders operations
    """
    def get_printers(self, **kwargs):
        # Create the query object
        query = Printer.query

        # Filter by the given kwargs
        for key, value in kwargs.items():
            if hasattr(Printer, key):
                if key in ("id", "name", "serialNumber", "apiKey"):
                    return self.execute_query(query.filter_by(**{key: value}), use_list=False)
                else:
                    query = query.filter_by(**{key: value})
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Return all the filtered items
        return self.execute_query(query)

    def update_printer(self, printer: Printer, **kwargs):
        # Modify the specified job fields
        for key, value in kwargs.items():
            if hasattr(Printer, key):
                setattr(printer, key, value)
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return printer

    def add_finished_print(self, printer: Printer, success: bool, printing_time: timedelta):
        # Initialize the values to update dictionary
        values_to_update = {Printer.totalPrintingTime: Printer.totalPrintingTime + printing_time}

        # Decide if we will need to increment the succeed or failed prints counter
        if success:
            values_to_update[Printer.totalSuccessPrints] = Printer.totalSuccessPrints + 1
        else:
            values_to_update[Printer.totalFailedPrints] = Printer.totalFailedPrints + 1

        # Update the values in the database
        self.execute_update(Printer.query.filter_by(id=printer.id), values_to_update)
