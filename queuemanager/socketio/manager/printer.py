"""
This module implements the printer namespace manager class.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.2"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .base_class import SocketIOManagerBase


class PrinterNamespaceManager(SocketIOManagerBase):
    """
    This class defines the printer namespace and the events that the server will be listening for.
    """
    def _check_jobs_in_queue(self, printer):
        # If the printer has an assigned job already, don't assign any job to it
        if printer.current_job:
            return

        # Check if there is any job in the queue and send it to the printer
        job = self.db_manager.get_first_job_in_queue()

        if job is not None:
            self.assign_job_to_printer(job, printer)

    def _update_printer_state(self, printer, new_state_str):
        # Update the printer state in the socketio_printer
        self.db_manager.update_printer(printer, idState=self.db_manager.printer_state_ids[new_state_str])
        self.app.logger.info("Printer state changed. New state: {}".format(new_state_str))

    def _update_printer_extruders(self, printer, extruders_info):
        for extruder in extruders_info:
            # Init the dictionary of the values to update
            values_to_update = dict()
            # Get the extruder object from the socketio_printer
            extruder_obj = self.db_manager.get_printer_extruders(printer=printer, index=extruder["index"])[0]

            if "material" in extruder.keys():
                values_to_update["material"] = extruder["material"]
            if "extruder_type" in extruder.keys():
                values_to_update["type"] = extruder["extruder_type"]

            # Update the extruder data
            self.db_manager.update_printer_extruder(extruder_obj, **values_to_update)
            self.app.logger.info("Printer extruder information changed. New information: {}".format(extruder_obj))

    def _repair_printing_jobs(self, printer, new_state_str):
        job = printer.current_job

        if job.state.stateString == "Waiting" and new_state_str == "Ready":
            self.printer_namespace.emit_print_job(job, printer.sid)
        elif new_state_str == "Print finished" and job.state.stateString == "Finished":
            return
        elif job.state.stateString == "Printing" and new_state_str != "Printing":
            self.db_manager.set_finished_job(job)
            if new_state_str != "Print finished":
                self.db_manager.update_job(job, interrupted=True)
            self.client_namespace.emit_job_progress_updated(job, broadcast=True)
            self.client_namespace.emit_jobs_updated(broadcast=True)

        if new_state_str != "Print finished" and job.state.stateString == "Finished":
            self.printer_namespace.emit_job_recovered(job, sid=printer.sid)

    def printer_connected(self, sid, ip_address):
        # Get the printer object
        printer = self.db_manager.get_printers(id=1)

        # Check that the printer is not connected already
        if printer.state.id != self.db_manager.printer_state_ids["Offline"]:
            # If the printer is connected already, reject the new connection
            return False
        else:
            # Set the sid as the printer sid
            self.db_manager.update_printer(printer, sid=sid, ipAddress=ip_address)
            return True

    def printer_disconnected(self, sid):
        # Get the printer object
        printer = self.db_manager.get_printers(id=1)

        # Change the printer state to offline
        if printer.sid == sid:
            self.printer_state_updated("Offline")
            self.db_manager.update_printer(printer, sid=None, ipAddress=None)

    def printer_initial_data(self, state, extruders_info):
        # Get the printer object
        printer = self.db_manager.get_printers(id=1)

        # If the printer isn't in Offline state, reject the initial data so isn't the real initial data
        if printer.state.stateString != "Offline":
            return

        self._update_printer_state(printer, state)
        self._update_printer_extruders(printer, extruders_info)

        self.client_namespace.emit_printer_data_updated(printer, broadcast=True)

        if printer.state.isOperationalState:
            self.db_manager.update_can_be_printed_jobs()
            self.client_namespace.emit_jobs_updated(broadcast=True)

        # If the printer came from the 'Offline' state and the new state is not 'Printing' or the new state is 'Error',
        # enqueue again the Printing job (if any) of this printer
        if printer.current_job and state != "Printing":
            self._repair_printing_jobs(printer, state)

        # If the new state is 'Ready', check if there is any job in the queue and send it to the printer
        if printer.state.stateString == "Ready":
            self._check_jobs_in_queue(printer)

    def printer_state_updated(self, state):
        # Get the printer object
        printer = self.db_manager.get_printers(id=1)

        self._update_printer_state(printer, state)

        self.client_namespace.emit_printer_data_updated(printer, broadcast=True)

        self.db_manager.update_can_be_printed_jobs()
        self.client_namespace.emit_jobs_updated(broadcast=True)

        # If the new state is 'Ready', check if there is any job in the queue and send it to the printer
        if printer.state.stateString == "Ready":
            self._check_jobs_in_queue(printer)

    def printer_extruders_updated(self, extruders_info):
        # Get the printer object
        printer = self.db_manager.get_printers(id=1)

        self._update_printer_extruders(printer, extruders_info)

        self.client_namespace.emit_printer_data_updated(printer, broadcast=True)

        if printer.state.isOperationalState:
            self.db_manager.update_can_be_printed_jobs()
            self.client_namespace.emit_jobs_updated(broadcast=True)

        # Recheck can be printed jobs and jobs in queue, only if the printer is in ready state
        if printer.state.stateString == "Ready":
            self._check_jobs_in_queue(printer)

    def print_started(self, job_id):
        # Get the job object from the socketio_printer
        job_obj = self.db_manager.get_jobs(id=job_id)

        # Update the job state from 'Waiting' to 'Printing'
        self.db_manager.set_printing_job(job_obj)
        self.app.logger.info("Job '{}' state changed to 'Printing'".format(job_obj))

        self.client_namespace.emit_jobs_updated(broadcast=True)

    def print_finished(self, job_id, cancelled):
        # Get the job object from the socketio_printer
        job_obj = self.db_manager.get_jobs(id=job_id)

        # Update the job state from 'Waiting' to 'Printing'
        self.db_manager.set_finished_job(job_obj)
        self.app.logger.info("Job '{}' state changed to 'Finished'".format(job_obj))

        if cancelled:
            self.db_manager.update_job(job_obj, interrupted=True)

        self.client_namespace.emit_job_progress_updated(job_obj, broadcast=True)
        self.client_namespace.emit_jobs_updated(broadcast=True)

    def print_feedback(self, job_id, feedback_data):
        # Get the job object from the socketio_printer
        job_obj = self.db_manager.get_jobs(id=job_id)

        self.app.logger.info("Job {} feedback received.".format(job_obj))

        # Get the printer object
        printer = job_obj.assigned_printer

        if feedback_data["success"] or feedback_data["max_priority"] is None:
            self.db_manager.set_done_job(job_obj, feedback_data["success"])
            self.app.logger.info("Job '{}' state changed to 'Done'".format(job_obj))
        else:
            self.db_manager.enqueue_printing_or_finished_job(job_obj, feedback_data["max_priority"])
            self.app.logger.info("Job '{}' state changed to 'Waiting'".format(job_obj))

        # Update the printer statistics
        self.db_manager.add_finished_print(printer, feedback_data["success"], feedback_data["printing_time"])

        self.client_namespace.emit_printer_data_updated(printer, broadcast=True)
        self.client_namespace.emit_jobs_updated(broadcast=True)

    def printer_temperatures_updated(self, bed_temp, extruders_temp):
        info_str = "New printer temperatures -> bed: {}".format(str(bed_temp))
        for extruder_temp in extruders_temp:
            info_str += " / extruder {}: {}".format(extruder_temp["index"], extruder_temp["temp_value"])

        self.app.logger.debug(info_str)

        self.client_namespace.emit_printer_temperatures_updated(bed_temp, extruders_temp, broadcast=True)

    def job_progress_updated(self, id, progress, estimated_time_left, **_kwargs):
        # Get the job object from the socketio_printer
        job_obj = self.db_manager.get_jobs(id=id)

        self.app.logger.debug("New printing job (id={}) progress update -> progress: {}% / estimated_time_left: {}".
                              format(str(id), str(progress), str(estimated_time_left)))

        self.db_manager.update_job(job_obj, progress=progress, estimatedTimeLeft=estimated_time_left)

        self.client_namespace.emit_job_progress_updated(job_obj, broadcast=True)
