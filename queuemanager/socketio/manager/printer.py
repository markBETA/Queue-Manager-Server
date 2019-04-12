"""
This module implements the printer namespace manager class.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask import current_app

from .base_class import SocketIOManagerBase
from ...database import db_mgr


# TODO: Improve error detection and required actions

class PrinterNamespaceManager(SocketIOManagerBase):
    """
    This class defines the printer namespace and the events that the server will be listening for.
    """
    def __init__(self):
        super().__init__()

    def _check_jobs_in_queue(self):
        # Check if there is any job in the queue and send it to the printer
        job = db_mgr.get_first_job_in_queue()

        if job is not None:
            self.printer_namespace.emit_print_job(job)

    def _update_printer_state(self, printer, new_state_str):
        # If the printer came from the 'Offline' state and the new state is not 'Printing' or the new state is 'Error',
        # enqueue again the Printing job (if any) of this printer
        if (printer.state.stateString == "Offline" and new_state_str != "Printing") or new_state_str == "Error":
            self._repair_printing_jobs(new_state_str)

        # Update the printer state in the database
        db_mgr.update_printer(printer, idState=db_mgr.printer_state_ids[new_state_str])
        current_app.logger.info("Printer state changed. New state: {}".format(new_state_str))

    @staticmethod
    def _update_printer_extruders(printer, extruders_info):
        for extruder in extruders_info:
            # Init the dictionary of the values to update
            values_to_update = dict()
            # Get the extruder object from the database
            extruder_obj = db_mgr.get_printer_extruders(printer=printer, index=extruder["index"])[0]

            if "material" in extruder.keys():
                values_to_update["material"] = extruder["material"]
            if "extruder_type" in extruder.keys():
                values_to_update["type"] = extruder["extruder_type"]

            # Update the extruder data
            db_mgr.update_printer_extruder(extruder_obj, **values_to_update)
            current_app.logger.info("Printer extruder information changed. New information: {}".format(extruder_obj))

    def _repair_printing_jobs(self, new_state_str):
        # Check if there is any print job in Printing state
        jobs = db_mgr.get_jobs(idState=db_mgr.job_state_ids["Printing"])
        if jobs:
            for job in jobs:
                if new_state_str == "Print finished":
                    db_mgr.set_finished_job(job)
                else:
                    db_mgr.enqueue_printing_or_finished_job(job, max_priority=True)
                current_app.logger.info("Job {} recovered from a printing disconnection.".format(str(job)))
            self.client_namespace.emit_jobs_updated(broadcast=True)

    def printer_connected(self, sid):
        # Get the printer object
        printer = db_mgr.get_printers(id=1)

        # Check that the printer is not connected already
        if printer.state.id != db_mgr.printer_state_ids["Offline"]:
            # If the printer is connected already, reject the new connection
            return False
        else:
            # Set the sid as the printer sid
            db_mgr.update_printer(printer, sid=sid)
            self.client_namespace.emit_printer_data_updated(printer, broadcast=True)
            return True

    def printer_disconnected(self, sid):
        # Get the printer object
        printer = db_mgr.get_printers(id=1)

        # Change the printer state to offline
        if printer.sid == sid:
            db_mgr.update_printer(printer, idState=db_mgr.printer_state_ids["Offline"])
            current_app.logger.info("Printer state changed. New state: Offline")
            self.client_namespace.emit_printer_data_updated(printer, broadcast=True)
            db_mgr.update_can_be_printed_jobs()
            self.client_namespace.emit_jobs_updated(broadcast=True)

    def printer_initial_data(self, state, extruders_info):
        # Get the printer object
        printer = db_mgr.get_printers(id=1)

        self._update_printer_state(printer, state)
        self._update_printer_extruders(printer, extruders_info)
        self.client_namespace.emit_printer_data_updated(printer, broadcast=True)

        db_mgr.update_can_be_printed_jobs()
        self.client_namespace.emit_jobs_updated(broadcast=True)

        # If the new state is 'Ready', check if there is any job in the queue and send it to the printer
        if state == "Ready":
            self._check_jobs_in_queue()

    def printer_state_updated(self, state):
        # Get the printer object
        printer = db_mgr.get_printers(id=1)

        self._update_printer_state(printer, state)
        self.client_namespace.emit_printer_data_updated(printer, broadcast=True)

        # If the new state is 'Ready', check if there is any job in the queue and send it to the printer
        if state == "Ready":
            db_mgr.update_can_be_printed_jobs()
            self.client_namespace.emit_jobs_updated(broadcast=True)
            self._check_jobs_in_queue()

    def printer_extruders_updated(self, extruders_info):
        # Get the printer object
        printer = db_mgr.get_printers(id=1)

        self._update_printer_extruders(printer, extruders_info)
        self.client_namespace.emit_printer_data_updated(printer, broadcast=True)

        # Recheck can be printed jobs and jobs in queue
        db_mgr.update_can_be_printed_jobs()
        self.client_namespace.emit_jobs_updated(broadcast=True)
        self._check_jobs_in_queue()

    def print_started(self, job_id):
        # Get the job object from the database
        job_obj = db_mgr.get_jobs(id=job_id)

        # Update the job state from 'Waiting' to 'Printing'
        db_mgr.set_printing_job(job_obj)
        current_app.logger.info("Job '{}' state changed to 'Printing'".format(job_obj))

        self.client_namespace.emit_job_started(job_obj, broadcast=True)
        self.client_namespace.emit_jobs_updated(broadcast=True)

    def print_finished(self, job_id):
        # Get the job object from the database
        job_obj = db_mgr.get_jobs(id=job_id)

        # Update the job state from 'Waiting' to 'Printing'
        db_mgr.set_finished_job(job_obj)
        current_app.logger.info("Job '{}' state changed to 'Finished'".format(job_obj))

        # Update the job extruders with the used extruder type and material
        printer = db_mgr.get_printers(id=1)
        db_mgr.set_job_used_data_from_printer(job_obj, printer)

        self.client_namespace.emit_jobs_updated(broadcast=True)

    def print_feedback(self, job_id, feedback_data):
        # Get the printer object
        printer = db_mgr.get_printers(id=1)

        # Get the job object from the database
        job_obj = db_mgr.get_jobs(id=job_id)

        if feedback_data["success"] or feedback_data["max_priority"] is None:
            db_mgr.set_done_job(job_obj, feedback_data["success"])
            current_app.logger.info("Job '{}' state changed to 'Done'".format(job_obj))
        else:
            db_mgr.enqueue_printing_or_finished_job(job_obj, feedback_data["max_priority"])
            current_app.logger.info("Job '{}' state changed to 'Waiting'".format(job_obj))

        # Update the printer statistics
        db_mgr.add_finished_print(printer, feedback_data["success"], feedback_data["printing_time"])

        self.client_namespace.emit_printer_data_updated(printer, broadcast=True)
        self.client_namespace.emit_job_done(job_obj, broadcast=True)
        self.client_namespace.emit_jobs_updated(broadcast=True)

    def printer_temperatures_updated(self, bed_temp, extruders_temp):
        info_str = "New printer temperatures -> bed: {}".format(str(bed_temp))
        for extruder_temp in extruders_temp:
            info_str += " / extruder {}: {}".format(extruder_temp["index"], extruder_temp["temp_value"])

        current_app.logger.info(info_str)

        self.client_namespace.emit_printer_temperatures_updated(bed_temp, extruders_temp, broadcast=True)

    def job_progress_updated(self, job_id, progress, estimated_time_left):
        current_app.logger.info("New printing job (id={}) progress update -> progress: {}% / estimated time left {}".
                                format(str(job_id), str(progress), str(estimated_time_left)))

        self.client_namespace.emit_job_progress_updated(job_id, progress, estimated_time_left, broadcast=True)
