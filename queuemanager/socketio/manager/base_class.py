"""
This module contains the socketio manager base class.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from ...database import DBManager, Job, Printer
from ...file_storage import FileManager


class SocketIOManagerBase(object):
    """
    This class implements the socketio_printer manager base class
    """

    def __init__(self, db_manager: DBManager = None, file_manager: FileManager = None):
        self.client_namespace = None
        self.printer_namespace = None
        self.app = None

        # Set the DBManager object
        if db_manager is None:
            from ...database import db_mgr
            self.db_manager = db_mgr
        else:
            self.db_manager = db_manager

        # Set the FileManager object
        if file_manager is None:
            from ...file_storage import file_mgr
            self.file_manager = file_mgr
        else:
            self.file_manager = file_manager

    def init_app(self, app):
        self.app = app

    def set_client_namespace(self, client_namespace):
        self.client_namespace = client_namespace

    def set_printer_namespace(self, printer_namespace):
        self.printer_namespace = printer_namespace

    def set_db_manager(self, db_manager):
        self.db_manager = db_manager

    def assign_job_to_printer(self, job: Job, printer: Printer = None, send_after_assign: bool = True):
        if printer is None:
            # Get the printers that can print this job
            usable_printers = self.db_manager.check_can_be_printed_job(job, return_usable_printers=True)

            # If there is no usable printer for this job, return
            if not usable_printers:
                return

            # Take the first usable printer and assign it to the job
            printer = None
            for usable_printer in usable_printers:
                if usable_printer.idCurrentJob is None and usable_printer.state.stateString == "Ready":
                    printer = usable_printer
                    break

            # Check that there is at least one usable printer without an assigned print
            if printer is None:
                return

        self.db_manager.assign_job_to_printer(printer, job)

        if send_after_assign:
            self.printer_namespace.emit_print_job(job, printer.sid)
