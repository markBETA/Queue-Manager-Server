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

from ...database import db_mgr, DBManagerError
from ...file_storage import file_mgr
from ...file_storage.exceptions import (
    MissingHeaderKeys, InvalidFileHeader
)
from flask import current_app, request
from flask_socketio import Namespace, emit


class ClientNamespace(Namespace):
    """
    This class defines the client namespace and the events that the server will be listening for.
    """
    def emit_jobs_updated(self, data=None, broadcast: bool = False):
        emit("jobs_updated", data, broadcast=broadcast, namespace=self.namespace)

    def emit_job_analyze_error(self, data=None, broadcast: bool = False):
        emit("job_analyze_error", data, broadcast=broadcast, namespace=self.namespace)

    def emit_job_enqueue_error(self, data=None, broadcast: bool = False):
        emit("job_enqueue_error", data, broadcast=broadcast, namespace=self.namespace)

    @staticmethod
    def on_connect():
        current_app.logger.info("client %s connected", request.sid)

    @staticmethod
    def on_disconnect():
        current_app.logger.info("client %s disconnected", request.sid)

    def on_analyze_job(self, job_id: int):
        try:
            job = db_mgr.get_jobs(id=job_id)
        except DBManagerError as e:
            self.emit_job_analyze_error(str(e))
            return

        if job is None:
            self.emit_job_analyze_error("There is no job with this ID in the database")
            return

        try:
            # Retrieve the file header
            file_mgr.retrieve_file_header(job.file)
            # Get the job allowed configuration from the file header
            file_mgr.set_job_allowed_config_from_header(job)
        except (MissingHeaderKeys, InvalidFileHeader) as e:
            self.emit_job_analyze_error(str(e))
            return
        except DBManagerError:
            self.emit_job_analyze_error("Can't save the retrieved file header at the database")
            return

        self.emit_jobs_updated(broadcast=True)

    def on_enqueue_job(self, job_id: int):
        try:
            job = db_mgr.get_jobs(id=job_id)
            if job is not None:
                db_mgr.enqueue_created_job(job)
            else:
                self.emit_job_enqueue_error("There is no job with this ID in the database")
        except DBManagerError as e:
            self.emit_job_enqueue_error(str(e))

        self.emit_jobs_updated(broadcast=True)


client_namespace = ClientNamespace("/client")
