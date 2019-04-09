"""
This module implements the printer namespace class.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

import json

from flask import current_app, request
from flask_socketio import Namespace, emit

from ...database import Job


class PrinterNamespace(Namespace):
    """
    This class defines the printer namespace and the events that the server will be listening for.
    """
    def __init__(self, socketio_manager, namespace=None):
        super().__init__(namespace)
        self.socketio_manager = socketio_manager

    def emit_print_job(self, job: Job, broadcast: bool = False):
        data = {"job_id": job.id, "file_id": job.file.id}
        emit("print_job", data, broadcast=broadcast, namespace=self.namespace)

    def on_connect(self):
        current_app.logger.info("Printer connected")
        self.socketio_manager.printer_connected(request.sid)

    def on_disconnect(self):
        current_app.logger.info("Printer disconnected")
        self.socketio_manager.printer_disconnected(request.sid)

    def on_initial_data(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        self.socketio_manager.printer_initial_data(data["state"], data["extruders_info"])

    def on_state_updated(self, new_state_str):
        self.socketio_manager.printer_state_updated(new_state_str)

    def on_extruders_updated(self, extruders_info):
        if isinstance(extruders_info, str):
            extruders_info = json.loads(extruders_info)
        self.socketio_manager.printer_extruders_updated(extruders_info)

    def on_print_started(self, job_id):
        self.socketio_manager.print_started(job_id)

    def on_print_finished(self, job_id):
        self.socketio_manager.print_finished(job_id)

    def on_print_feedback(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        try:
            self.socketio_manager.print_feedback(data["job_id"], data["feedback_data"])
        except KeyError:
            current_app.logger.error("Invalid 'print_feedback' event data")
