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

from datetime import timedelta

from sqlalchemy.orm import scoped_session

from .base_class import DBManagerBase
from .exceptions import (
    InvalidParameter
)
from ..models import (
    PrinterModel, PrinterState, PrinterExtruderType, PrinterMaterial, PrinterExtruder,
    Printer, Job
)


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
    def __init__(self, autocommit: bool = True, override_session: scoped_session = None):
        super().__init__(autocommit, override_session)
        self.printer_state_ids = dict()

    def init_static_values(self):
        for state in self.get_printer_states():
            self.printer_state_ids[state.stateString] = state.id

    def init_printers_state(self):
        # Disable the autocommit (if enabled)
        self._set_autocommit(False)

        for printer in self.get_printers():
            self.update_printer(printer, idState=self.printer_state_ids["Offline"])

        # Restore the autocommit initial value
        self._restore_autocommit()

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

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
        values_to_update = {Printer.totalPrintingTime: printer.totalPrintingTime + printing_time}

        # Decide if we will need to increment the succeed or failed prints counter
        if success:
            values_to_update[Printer.totalSuccessPrints] = Printer.totalSuccessPrints + 1
        else:
            values_to_update[Printer.totalFailedPrints] = Printer.totalFailedPrints + 1

        # Update the values in the database
        self.execute_update(Printer.query.filter_by(id=printer.id), values_to_update)

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

    def assign_job_to_printer(self, printer: Printer, job: Job):
        # Check that the job is in the 'Waiting'
        if job.state.stateString != "Waiting":
            raise InvalidParameter("The job to assign needs to be in the state 'Waiting''")
        # Check also if the job can be printed before assign it
        if not job.canBePrinted:
            raise InvalidParameter('Can\'t assign a job to a printer that can\'t be printed')

        self.update_printer(printer, idCurrentJob=job.id)

        return printer
