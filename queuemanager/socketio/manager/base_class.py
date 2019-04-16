"""
This module contains the database manager base class.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from ...database import db_mgr, Job, Printer


class SocketIOManagerBase(object):
    """
    This class implements the database manager base class
    """

    def __init__(self):
        self.client_namespace = None
        self.printer_namespace = None

    def set_client_namespace(self, client_namespace):
        self.client_namespace = client_namespace

    def set_printer_namespace(self, printer_namespace):
        self.printer_namespace = printer_namespace

    def assign_job_to_printer(self, job: Job, printer: Printer = None, send_after_assign: bool = True):
        if printer is None:
            # Get the printers that can print this job
            usable_printers = db_mgr.check_can_be_printed_job(job, return_usable_printers=True)

            # If there is no usable printer for this job, return
            if not usable_printers:
                return

            # Take the first usable printer and assign it to the job
            printer = usable_printers[0]

        db_mgr.update_printer(printer, idCurrentJob=job.id)

        if send_after_assign:
            self.printer_namespace.emit_print_job(job, printer.sid)
