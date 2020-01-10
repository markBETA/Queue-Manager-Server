"""
This module implements the printer namespace class.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

import uuid

from flask import request, session
from flask_socketio import disconnect

from .base_class import Namespace
from ..auth import socketio_auth_required
from ..schemas import (
    EmitPrintJobSchema, EmitJobRecoveredSchema, OnInitialDataSchema, OnStateUpdatedSchema, OnExtrudersUpdatedSchema,
    OnPrintStartedSchema, OnPrintFinishedSchema, OnPrintFeedbackSchema, OnPrinterTemperaturesUpdatedSchema,
    OnJobProgressUpdatedSchema
)
from ...database import Job, DBManagerError


class PrinterNamespace(Namespace):
    """
    This class defines the printer namespace and the events that the server will be listening for.
    """
    def __init__(self, socketio, socketio_manager, namespace=None):
        super().__init__(namespace)
        self.socketio = socketio
        self.socketio_manager = socketio_manager

        # Schema objects
        self.emit_print_job_schema = EmitPrintJobSchema()
        self.emit_job_recovered_schema = EmitJobRecoveredSchema()
        self.on_initial_data_schema = OnInitialDataSchema()
        self.on_state_updated_schema = OnStateUpdatedSchema()
        self.on_extruders_updated_schema = OnExtrudersUpdatedSchema()
        self.on_print_started_schema = OnPrintStartedSchema()
        self.on_print_finished_schema = OnPrintFinishedSchema()
        self.on_print_feedback_schema = OnPrintFeedbackSchema()
        self.on_printer_temperatures_updated_schema = OnPrinterTemperaturesUpdatedSchema()
        self.on_job_progress_updated_schema = OnJobProgressUpdatedSchema()

    def _emit(self, event, *args, **kwargs):
        if 'namespace' in kwargs:
            namespace = kwargs['namespace']
        else:
            namespace = self.namespace
        callback = kwargs.get('callback')
        broadcast = kwargs.get('broadcast')
        room = kwargs.get('room')
        if room is None and not broadcast:
            room = request.sid
        include_self = kwargs.get('include_self', True)
        ignore_queue = kwargs.get('ignore_queue', False)

        self.socketio.emit(event, *args, namespace=namespace, room=room,
                           include_self=include_self, callback=callback,
                           ignore_queue=ignore_queue)

    def emit_print_job(self, job: Job, sid: str = None, broadcast: bool = False):
        """
        Emit the event 'print_job'. The data send is defined by
        :class:`EmitPrintJobSchema`
        """
        serialized_data = self.emit_print_job_schema.dump(job)

        if not serialized_data.errors:
            self._emit("print_job", serialized_data.data, room=sid, broadcast=broadcast)
        else:
            self._log_event_processing_error("print_job", serialized_data.errors)

    def emit_job_recovered(self, job: Job, sid: str = None, broadcast: bool = False):
        """
        Emit the event 'job_recovered'. The data send is defined by
        :class:`EmitJobRecoveredSchema`
        """
        serialized_data = self.emit_job_recovered_schema.dump(job)

        if not serialized_data.errors:
            self._emit("job_recovered", serialized_data.data, room=sid, broadcast=broadcast)
        else:
            self._log_event_processing_error("job_recovered", serialized_data.errors)

    def on_connect(self):
        """
        Event called when the printer is connected
        """
        if set(session["identity"].keys()) != {"type", "id", "serial_number"}:
            self.app.logger.info("Detected invalid identity data. Disconnecting SID '{}'".format(request.sid))
            disconnect()
            return

        if session["identity"]["type"] != "printer":
            self.app.logger.info("Detected invalid identity type. Disconnecting SID '{}'".format(request.sid))
            disconnect()
            return

        try:
            old_sid = self.socketio_manager.printer_connected(request.sid, request.remote_addr)
        except DBManagerError as e:
            self.app.logger.error("Unable to update the printer connection at the database. Details: " + str(e))
            disconnect()
            return

        # If the printer from the identity data already has got a SID, disconnect that SID first
        if old_sid is not None:
            disconnect(sid=old_sid)

        # Send the session key to the printer
        session["key"] = str(uuid.uuid4())
        self._emit("session_key", session["key"])

        self.app.logger.info("Printer connected")

    def on_disconnect(self):
        """
        Event called when the printer is disconnected
        """
        try:
            self.socketio_manager.printer_disconnected(request.sid)
        except DBManagerError as e:
            self.app.logger.error("Unable to save the printer disconnection at the database. Details: " + str(e))
            return

        self.app.logger.info("Printer disconnected")

    @socketio_auth_required
    def on_initial_data(self, data: dict):
        """
        Listen for the event 'initial_data'. The data expected is defined by
        :class:`OnInitialDataSchema`
        """
        deserialized_data = self.on_initial_data_schema.load(data)

        if not deserialized_data.errors:
            try:
                self.socketio_manager.printer_initial_data(**deserialized_data.data)
            except DBManagerError as e:
                self.app.logger.error("Unable to save the printer initial data at the database. Details: " + str(e))
        else:
            self._log_event_processing_error("initial_data", deserialized_data.errors)

    @socketio_auth_required
    def on_state_updated(self, data: dict):
        """
        Listen for the event 'state_updated'. The data expected is defined by
        :class:`OnStateUpdatedSchema`
        """
        deserialized_data = self.on_state_updated_schema.load(data)

        if not deserialized_data.errors:
            try:
                self.socketio_manager.printer_state_updated(**deserialized_data.data)
            except DBManagerError as e:
                self.app.logger.error("Unable to save the printer state update data at the database. "
                                      "Details: " + str(e))
        else:
            self._log_event_processing_error("state_updated", deserialized_data.errors)

    @socketio_auth_required
    def on_extruders_updated(self, data: dict):
        """
        Listen for the event 'extruders_updated'. The data expected is defined by
        :class:`OnExtrudersUpdatedSchema`
        """
        deserialized_data = self.on_extruders_updated_schema.load(data)

        if not deserialized_data.errors:
            try:
                self.socketio_manager.printer_extruders_updated(**deserialized_data.data)
            except DBManagerError as e:
                self.app.logger.error("Unable to save the printer extruders update data at the database. "
                                      "Details: " + str(e))
        else:
            self._log_event_processing_error("extruders_updated", deserialized_data.errors)

    @socketio_auth_required
    def on_print_started(self, data: dict):
        """
        Listen for the event 'print_started'. The data expected is defined by
        :class:`OnPrintStartedSchema`
        """
        deserialized_data = self.on_print_started_schema.load(data)

        if not deserialized_data.errors:
            try:
                self.socketio_manager.print_started(**deserialized_data.data)
            except DBManagerError as e:
                self.app.logger.error("Unable to update the started print state at the database. "
                                      "Details: " + str(e))
        else:
            self._log_event_processing_error("print_started", deserialized_data.errors)

    @socketio_auth_required
    def on_print_finished(self, data: dict):
        """
        Listen for the event 'print_finished'. The data expected is defined by
        :class:`OnPrintFinishedSchema`
        """
        deserialized_data = self.on_print_finished_schema.load(data)

        if not deserialized_data.errors:
            try:
                self.socketio_manager.print_finished(**deserialized_data.data)
            except DBManagerError as e:
                self.app.logger.error("Unable to update the finished print state at the database. "
                                      "Details: " + str(e))
        else:
            self._log_event_processing_error("print_finished", deserialized_data.errors)

    @socketio_auth_required
    def on_print_feedback(self, data: dict):
        """
        Listen for the event 'print_finished'. The data expected is defined by
        :class:`OnPrintFeedbackSchema`
        """
        deserialized_data = self.on_print_feedback_schema.load(data)

        if not deserialized_data.errors:
            try:
                self.socketio_manager.print_feedback(**deserialized_data.data)
            except DBManagerError as e:
                self.app.logger.error("Unable to save the finished print feedback at the database. "
                                      "Details: " + str(e))
        else:
            self._log_event_processing_error("print_feedback", deserialized_data.errors)

    @socketio_auth_required
    def on_printer_temperatures_updated(self, data: dict):
        """
        Listen for the event 'printer_temperatures_updated'. The data expected is defined by
        :class:`OnPrinterTemperaturesUpdatedSchema`
        """
        deserialized_data = self.on_printer_temperatures_updated_schema.load(data)

        if not deserialized_data.errors:
            try:
                self.socketio_manager.printer_temperatures_updated(**deserialized_data.data)
            except DBManagerError as e:
                self.app.logger.error("Unable to save printer temperatures update at the database. "
                                      "Details: " + str(e))
        else:
            self._log_event_processing_error("printer_temperatures_updated", deserialized_data.errors)

    @socketio_auth_required
    def on_job_progress_updated(self, data: dict):
        """
        Listen for the event 'job_progress_updated'. The data expected is defined by
        :class:`OnJobProgressUpdatedSchema`
        """
        deserialized_data = self.on_job_progress_updated_schema.load(data)

        if not deserialized_data.errors:
            try:
                self.socketio_manager.job_progress_updated(**deserialized_data.data)
            except DBManagerError as e:
                self.app.logger.error("Unable to save the current job progress update at the database. "
                                      "Details: " + str(e))
        else:
            self._log_event_processing_error("job_progress_updated", deserialized_data.errors)
