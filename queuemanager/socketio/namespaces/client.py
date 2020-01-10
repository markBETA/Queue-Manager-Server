"""
This module implements the client namespace class.
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
    EmitJobAnalyzeDoneSchema, EmitJobAnalyzeErrorSchema, EmitJobEnqueueDoneSchema, EmitJobEnqueueErrorSchema,
    EmitPrinterDataUpdatedSchema, EmitPrinterTemperaturesUpdatedSchema, EmitJobProgressUpdatedSchema,
    OnAnalyzeJobSchema, OnEnqueueJobSchema, EmitAnalyzeErrorHelper, EmitEnqueueErrorHelper,
    EmitPrinterTemperaturesUpdatedHelper
)
from ...database import Job, Printer, db_mgr


class ClientNamespace(Namespace):
    """
    This class defines the client namespace and the events that the server will be listening for.
    """
    def __init__(self, socketio, socketio_manager, namespace=None):
        super().__init__(namespace)
        self.socketio = socketio
        self.socketio_manager = socketio_manager

        # Schema objects
        self.emit_job_analyze_done_schema = EmitJobAnalyzeDoneSchema()
        self.emit_job_analyze_error_schema = EmitJobAnalyzeErrorSchema()
        self.emit_job_enqueue_done_schema = EmitJobEnqueueDoneSchema()
        self.emit_job_enqueue_error_schema = EmitJobEnqueueErrorSchema()
        self.emit_printer_data_updated_schema = EmitPrinterDataUpdatedSchema()
        self.emit_printer_temperatures_updated_schema = EmitPrinterTemperaturesUpdatedSchema()
        self.emit_job_progress_updated_schema = EmitJobProgressUpdatedSchema()
        self.on_analyze_job_schema = OnAnalyzeJobSchema()
        self.on_enqueue_job_schema = OnEnqueueJobSchema()

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

    def emit_jobs_updated(self, broadcast: bool = False):
        """
        Emit the event 'jobs_updated'. This event don't send any data in the payload.
        """
        self._emit("jobs_updated", broadcast=broadcast)

    def emit_job_analyze_done(self, job: Job, broadcast: bool = False):
        """
        Emit the event 'job_analyze_done'. The data send is defined by
        :class:`EmitJobAnalyzeDoneSchema`.
        """
        serialized_data = self.emit_job_analyze_done_schema.dump(job)

        if not serialized_data.errors:
            self._emit("job_analyze_done", serialized_data.data, broadcast=broadcast)
        else:
            self._log_event_processing_error("job_analyze_done", serialized_data.errors)

    def emit_job_analyze_error(self, job: Job, error_message: str, additional_info: dict = None,
                               broadcast: bool = False):
        """
        Emit the event 'job_analyze_error'. The data send is defined by
        :class:`EmitJobAnalyzeErrorSchema`.
        """
        helper = EmitAnalyzeErrorHelper(job, error_message, additional_info)
        serialized_data = self.emit_job_analyze_error_schema.dump(helper.__dict__)

        if not serialized_data.errors:
            self._emit("job_analyze_error", serialized_data.data, broadcast=broadcast)
        else:
            self._log_event_processing_error("job_analyze_error", serialized_data.errors)

    def emit_job_enqueue_done(self, job: Job, broadcast: bool = False):
        """
        Emit the event 'job_enqueue_done'. The data send is defined by
        :class:`EmitJobEnqueueDoneSchema`.
        """
        serialized_data = self.emit_job_enqueue_done_schema.dump(job)

        if not serialized_data.errors:
            self._emit("job_enqueue_done", serialized_data.data, broadcast=broadcast)
        else:
            self._log_event_processing_error("job_enqueue_done", serialized_data.errors)

    def emit_job_enqueue_error(self, job: Job, error_message: str, additional_info: dict = None,
                               broadcast: bool = False):
        """
        Emit the event 'job_enqueue_error'. The data send is defined by
        :class:`EmitJobEnqueueErrorSchema`.
        """
        helper = EmitEnqueueErrorHelper(job, error_message, additional_info)
        serialized_data = self.emit_job_enqueue_error_schema.dump(helper.__dict__)

        if not serialized_data.errors:
            self._emit("job_enqueue_error", serialized_data.data, broadcast=broadcast)
        else:
            self._log_event_processing_error("job_enqueue_error", serialized_data.errors)

    def emit_printer_data_updated(self, printer: Printer, broadcast: bool = False):
        """
        Emit the event 'printer_data_updated'. The data send is defined by
        :class:`EmitPrinterDataUpdatedSchema`
        """
        serialized_data = self.emit_printer_data_updated_schema.dump(printer)

        if not serialized_data.errors:
            self._emit("printer_data_updated", serialized_data.data, broadcast=broadcast)
        else:
            self._log_event_processing_error("printer_data_updated", serialized_data.errors)

    def emit_printer_temperatures_updated(self, bed_temp: float, extruders_temp: list, broadcast: bool = False):
        """
        Emit the event 'printer_temperatures_updated'. The data send is defined by
        :class:`EmitPrinterTemperaturesUpdatedSchema`
        """
        helper = EmitPrinterTemperaturesUpdatedHelper(bed_temp, extruders_temp)
        serialized_data = self.emit_printer_temperatures_updated_schema.dump(helper.__dict__)

        if not serialized_data.errors:
            self._emit("printer_temperatures_updated", serialized_data.data, broadcast=broadcast)
        else:
            self._log_event_processing_error("printer_temperatures_updated", serialized_data.errors)

    def emit_job_progress_updated(self, job: Job, broadcast: bool = False):
        """
        Emit the event 'job_progress_updated'. The data send is defined by
        :class:`EmitJobProgressUpdatedSchema`
        """
        serialized_data = self.emit_job_progress_updated_schema.dump(job)

        if not serialized_data.errors:
            self._emit("job_progress_updated", serialized_data.data, broadcast=broadcast)
        else:
            self._log_event_processing_error("job_progress_update", serialized_data.errors)

    def on_connect(self):
        """
        Event called when the client is connected
        """
        if set(session["identity"].keys()) != {"type", "id", "is_admin"}:
            self.app.logger.info("Detected invalid identity data. Disconnecting SID '{}'".format(request.sid))
            disconnect()
            return

        if session["identity"]["type"] != "user":
            self.app.logger.info("Detected invalid identity type. Disconnecting SID '{}'".format(request.sid))
            disconnect()
            return

        session["key"] = str(uuid.uuid4())
        self._emit("session_key", session["key"], broadcast=False)

        self.app.logger.info("Client %s connected", request.sid)

    def on_disconnect(self):
        """
        Event called when the client is disconnected
        """
        self.app.logger.info("Client %s disconnected", request.sid)

    @socketio_auth_required
    def on_analyze_job(self, data: dict):
        """
        Listen for the event 'analyze_job'. The data expected is defined by
        :class:`OnAnalyzeJob`
        """
        deserialized_data = self.on_analyze_job_schema.load(data)

        if not deserialized_data.errors:
            self.socketio_manager.analyze_job(**deserialized_data.data)
        else:
            try:
                job = db_mgr.get_jobs(id=deserialized_data.data["job_id"])
            except KeyError:
                job = None
            self.emit_job_analyze_error(job, "Corrupted event payload", deserialized_data.errors)

    @socketio_auth_required
    def on_enqueue_job(self, data: dict):
        """
        Listen for the event 'enqueue_job'. The data expected is defined by
        :class:`OnEnqueueJob`
        """
        deserialized_data = self.on_enqueue_job_schema.load(data)

        if not deserialized_data.errors:
            self.socketio_manager.enqueue_job(**deserialized_data.data)
        else:
            try:
                job = db_mgr.get_jobs(id=deserialized_data.data["job_id"])
            except KeyError:
                job = None
            self.emit_job_enqueue_error(job, "Corrupted event payload", deserialized_data.errors)
