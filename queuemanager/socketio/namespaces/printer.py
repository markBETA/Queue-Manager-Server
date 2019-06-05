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

import uuid

from flask import current_app, request, session
from flask_socketio import Namespace, emit

from ..definitions import socketio_auth_required
from ..schemas import (
    EmitPrintJobSchema, EmitJobRecoveredSchema, OnInitialDataSchema, OnStateUpdatedSchema, OnExtrudersUpdatedSchema,
    OnPrintStartedSchema, OnPrintFinishedSchema, OnPrintFeedbackSchema, OnPrinterTemperaturesUpdatedSchema,
    OnJobProgressUpdatedSchema
)
from ...database import Job


class PrinterNamespace(Namespace):
    """
    This class defines the printer namespace and the events that the server will be listening for.
    """
    def __init__(self, socketio_manager, namespace=None):
        super().__init__(namespace)
        self.socketio_manager = socketio_manager

    def emit_print_job(self, job: Job, sid: str = None, broadcast: bool = False):
        """
        Emit the event 'print_job'. The data send is defined by
        :class:`EmitPrintJobSchema`
        """
        serialized_data = EmitPrintJobSchema().dump(job)

        if not serialized_data.errors:
            emit("print_job", serialized_data.data, room=sid, broadcast=broadcast, namespace=self.namespace)
        else:
            # TODO: Send error notification
            pass

    def emit_job_recovered(self, job: Job, sid: str = None, broadcast: bool = False):
        """
        Emit the event 'job_recovered'. The data send is defined by
        :class:`EmitJobRecoveredSchema`
        """
        serialized_data = EmitJobRecoveredSchema().dump(job)

        if not serialized_data.errors:
            emit("job_recovered", serialized_data.data, room=sid, broadcast=broadcast, namespace=self.namespace)
        else:
            # TODO: Send error notification
            pass

    def on_connect(self):
        """
        Event called when the printer is connected
        """
        connection_allowed = self.socketio_manager.printer_connected(request.sid, request.remote_addr) and \
            session["identity"].get("type") == "printer"

        if connection_allowed:
            current_app.logger.info("Printer connected")
        else:
            current_app.logger.info("Printer already connected. New connection rejected")

        if connection_allowed:
            session["key"] = str(uuid.uuid4())
            emit("session_key", session["key"])

        return connection_allowed

    def on_disconnect(self):
        """
        Event called when the printer is disconnected
        """
        self.socketio_manager.printer_disconnected(request.sid)

        current_app.logger.info("Printer disconnected")

    @socketio_auth_required
    def on_initial_data(self, data: dict):
        """
        Listen for the event 'initial_data'. The data expected is defined by
        :class:`OnInitialDataSchema`
        """
        deserialized_data = OnInitialDataSchema().load(data)

        if not deserialized_data.errors:
            self.socketio_manager.printer_initial_data(**deserialized_data.data)
        else:
            # TODO: Send error notification
            pass

    @socketio_auth_required
    def on_state_updated(self, data: dict):
        """
        Listen for the event 'state_updated'. The data expected is defined by
        :class:`OnStateUpdatedSchema`
        """
        deserialized_data = OnStateUpdatedSchema().load(data)

        if not deserialized_data.errors:
            self.socketio_manager.printer_state_updated(**deserialized_data.data)
        else:
            # TODO: Send error notification
            pass

    @socketio_auth_required
    def on_extruders_updated(self, data: dict):
        """
        Listen for the event 'extruders_updated'. The data expected is defined by
        :class:`OnExtrudersUpdatedSchema`
        """
        deserialized_data = OnExtrudersUpdatedSchema().load(data)

        if not deserialized_data.errors:
            self.socketio_manager.printer_extruders_updated(**deserialized_data.data)
        else:
            # TODO: Send error notification
            pass

    @socketio_auth_required
    def on_print_started(self, data: dict):
        """
        Listen for the event 'print_started'. The data expected is defined by
        :class:`OnPrintStartedSchema`
        """
        deserialized_data = OnPrintStartedSchema().load(data)

        if not deserialized_data.errors:
            self.socketio_manager.print_started(**deserialized_data.data)
        else:
            # TODO: Send error notification
            pass

    @socketio_auth_required
    def on_print_finished(self, data: dict):
        """
        Listen for the event 'print_finished'. The data expected is defined by
        :class:`OnPrintFinishedSchema`
        """
        deserialized_data = OnPrintFinishedSchema().load(data)

        if not deserialized_data.errors:
            self.socketio_manager.print_finished(**deserialized_data.data)
        else:
            # TODO: Send error notification
            pass

    @socketio_auth_required
    def on_print_feedback(self, data: dict):
        """
        Listen for the event 'print_finished'. The data expected is defined by
        :class:`OnPrintFeedbackSchema`
        """
        deserialized_data = OnPrintFeedbackSchema().load(data)

        if not deserialized_data.errors:
            self.socketio_manager.print_feedback(**deserialized_data.data)
        else:
            # TODO: Send error notification
            pass

    @socketio_auth_required
    def on_printer_temperatures_updated(self, data: dict):
        """
        Listen for the event 'printer_temperatures_updated'. The data expected is defined by
        :class:`OnPrinterTemperaturesUpdatedSchema`
        """
        deserialized_data = OnPrinterTemperaturesUpdatedSchema().load(data)

        if not deserialized_data.errors:
            self.socketio_manager.printer_temperatures_updated(**deserialized_data.data)
        else:
            # TODO: Send error notification
            pass

    @socketio_auth_required
    def on_job_progress_updated(self, data: dict):
        """
        Listen for the event 'job_progress_updated'. The data expected is defined by
        :class:`OnJobProgressUpdatedSchema`
        """
        deserialized_data = OnJobProgressUpdatedSchema().load(data)

        if not deserialized_data.errors:
            self.socketio_manager.job_progress_updated(**deserialized_data.data)
        else:
            # TODO: Send error notification
            pass
