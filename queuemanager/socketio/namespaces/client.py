"""
This module implements the client namespace class.
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
from flask_socketio import Namespace, emit, disconnect

from ..definitions import socketio_auth_required
from ..schemas import (
    EmitJobAnalyzeDoneSchema, EmitJobAnalyzeErrorSchema, EmitJobEnqueueDoneSchema, EmitJobEnqueueErrorSchema,
    EmitPrinterDataUpdatedSchema, EmitPrinterTemperaturesUpdatedSchema, EmitJobProgressUpdatedSchema,
    OnAnalyzeJob, OnEnqueueJob, EmitAnalyzeErrorHelper, EmitEnqueueErrorHelper,
    EmitPrinterTemperaturesUpdatedHelper
)
from ...database import Job, Printer, db_mgr


class ClientNamespace(Namespace):
    """
    This class defines the client namespace and the events that the server will be listening for.
    """
    def __init__(self, socketio_manager, namespace=None):
        super().__init__(namespace)
        self.socketio_manager = socketio_manager

    def emit_jobs_updated(self, broadcast: bool = False):
        """
        Emit the event 'jobs_updated'. This event don't send any data in the payload.
        """
        emit("jobs_updated", broadcast=broadcast, namespace=self.namespace)

    def emit_job_analyze_done(self, job: Job, broadcast: bool = False):
        """
        Emit the event 'job_analyze_done'. The data send is defined by
        :class:`EmitJobAnalyzeDoneSchema`.
        """
        serialized_data = EmitJobAnalyzeDoneSchema().dump(job)

        if not serialized_data.errors:
            emit("job_analyze_done", serialized_data.data, broadcast=broadcast, namespace=self.namespace)
        else:
            # TODO: Send error notification
            pass

    def emit_job_analyze_error(self, job: Job, error_message: str, additional_info: dict = None,
                               broadcast: bool = False):
        """
        Emit the event 'job_analyze_error'. The data send is defined by
        :class:`EmitJobAnalyzeErrorSchema`.
        """
        helper = EmitAnalyzeErrorHelper(job, error_message, additional_info)
        serialized_data = EmitJobAnalyzeErrorSchema().dump(helper.__dict__)

        if not serialized_data.errors:
            emit("job_analyze_error", serialized_data.data, broadcast=broadcast, namespace=self.namespace)
        else:
            # TODO: Send error notification
            pass

    def emit_job_enqueue_done(self, job: Job, broadcast: bool = False):
        """
        Emit the event 'job_enqueue_done'. The data send is defined by
        :class:`EmitJobEnqueueDoneSchema`.
        """
        serialized_data = EmitJobEnqueueDoneSchema().dump(job)

        if not serialized_data.errors:
            emit("job_enqueue_done", serialized_data.data, broadcast=broadcast, namespace=self.namespace)
        else:
            # TODO: Send error notification
            pass

    def emit_job_enqueue_error(self, job: Job, error_message: str, additional_info: dict = None,
                               broadcast: bool = False):
        """
        Emit the event 'job_enqueue_error'. The data send is defined by
        :class:`EmitJobEnqueueErrorSchema`.
        """
        helper = EmitEnqueueErrorHelper(job, error_message, additional_info)
        serialized_data = EmitJobEnqueueErrorSchema().dump(helper.__dict__)

        if not serialized_data.errors:
            emit("job_enqueue_error", serialized_data.data, broadcast=broadcast, namespace=self.namespace)
        else:
            # TODO: Send error notification
            pass

    def emit_printer_data_updated(self, printer: Printer, broadcast: bool = False):
        """
        Emit the event 'printer_data_updated'. The data send is defined by
        :class:`EmitPrinterDataUpdatedSchema`
        """
        serialized_data = EmitPrinterDataUpdatedSchema().dump(printer)

        if not serialized_data.errors:
            emit("printer_data_updated", serialized_data.data, broadcast=broadcast, namespace=self.namespace)
        else:
            # TODO: Send error notification
            pass

    def emit_printer_temperatures_updated(self, bed_temp: float, extruders_temp: list, broadcast: bool = False):
        """
        Emit the event 'printer_temperatures_updated'. The data send is defined by
        :class:`EmitPrinterTemperaturesUpdatedSchema`
        """
        helper = EmitPrinterTemperaturesUpdatedHelper(bed_temp, extruders_temp)
        serialized_data = EmitPrinterTemperaturesUpdatedSchema().dump(helper.__dict__)

        if not serialized_data.errors:
            emit("printer_temperatures_updated", serialized_data.data, broadcast=broadcast, namespace=self.namespace)
        else:
            # TODO: Send error notification
            pass

    def emit_job_progress_updated(self, job: Job, broadcast: bool = False):
        """
        Emit the event 'job_progress_updated'. The data send is defined by
        :class:`EmitJobProgressUpdatedSchema`
        """
        serialized_data = EmitJobProgressUpdatedSchema().dump(job)

        if not serialized_data.errors:
            emit("job_progress_updated", serialized_data.data, broadcast=broadcast, namespace=self.namespace)
        else:
            # TODO: Send error notification
            pass

    def on_connect(self):
        """
        Event called when the client is connected
        """
        if session["identity"].get("type") != "user":
            current_app.logger.info("Detected invalid access token type. Disconnecting SID '{}'".format(request.sid))
            disconnect()

        session["key"] = str(uuid.uuid4())
        emit("session_key", session["key"], broadcast=False, namespace=self.namespace)

        current_app.logger.info("Client %s connected", request.sid)

    @staticmethod
    def on_disconnect():
        """
        Event called when the client is disconnected
        """
        current_app.logger.info("Client %s disconnected", request.sid)

    @socketio_auth_required
    def on_analyze_job(self, data: dict):
        """
        Listen for the event 'analyze_job'. The data expected is defined by
        :class:`OnAnalyzeJob`
        """
        deserialized_data = OnAnalyzeJob().load(data)

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
        deserialized_data = OnEnqueueJob().load(data)

        if not deserialized_data.errors:
            self.socketio_manager.enqueue_job(**deserialized_data.data)
        else:
            try:
                job = db_mgr.get_jobs(id=deserialized_data.data["job_id"])
            except KeyError:
                job = None
            self.emit_job_enqueue_error(job, "Corrupted event payload", deserialized_data.errors)
