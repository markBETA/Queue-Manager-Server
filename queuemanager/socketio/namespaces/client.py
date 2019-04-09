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

from flask import current_app, request
from flask_socketio import Namespace, emit

from ...database import Job


class ClientNamespace(Namespace):
    """
    This class defines the client namespace and the events that the server will be listening for.
    """
    def __init__(self, socketio_manager, namespace=None):
        super().__init__(namespace)
        self.socketio_manager = socketio_manager

    def emit_jobs_updated(self, broadcast: bool = False):
        emit("jobs_updated", broadcast=broadcast, namespace=self.namespace)

    def emit_job_analyze_done(self, job: Job, broadcast: bool = False):
        data = {"id": job.id, "name": job.name}
        emit("job_analyze_done", data, broadcast=broadcast, namespace=self.namespace)

    def emit_job_analyze_error(self, job, message, broadcast: bool = False):
        data = {"job": {"id": job.id, "name": job.name}, "message": message}
        emit("job_analyze_error", data, broadcast=broadcast, namespace=self.namespace)

    def emit_job_enqueue_done(self, job, broadcast: bool = False):
        data = {"id": job.id, "name": job.name}
        emit("job_enqueue_done", data, broadcast=broadcast, namespace=self.namespace)

    def emit_job_enqueue_error(self, job, message, broadcast: bool = False):
        data = {"job": {"id": job.id, "name": job.name}, "message": message}
        emit("job_enqueue_error", data, broadcast=broadcast, namespace=self.namespace)

    @staticmethod
    def on_connect():
        current_app.logger.info("Client %s connected", request.sid)

    @staticmethod
    def on_disconnect():
        current_app.logger.info("Client %s disconnected", request.sid)

    def on_analyze_job(self, job_id: int):
        self.socketio_manager.analyze_job(job_id)

    def on_enqueue_job(self, job_id: int):
        self.socketio_manager.enqueue_job(job_id)
