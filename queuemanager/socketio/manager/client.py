"""
This module implements the client namespace manager class.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .base_class import SocketIOManagerBase
from ...database import db_mgr, DBManagerError
from ...file_storage import file_mgr
from ...file_storage.exceptions import (
    MissingFileDataKeys, InvalidFileData
)


class ClientNamespaceManager(SocketIOManagerBase):
    """
    This class defines the client namespace and the events that the server will be listening for.
    """
    def analyze_job(self, job_id: int):
        try:
            job = db_mgr.get_jobs(id=job_id)
        except DBManagerError as e:
            self.client_namespace.emit_job_analyze_error(None, str(e))
            return

        if job is None:
            self.client_namespace.emit_job_analyze_error(job, "There is no job with this ID in the database")
            return

        try:
            # Retrieve the file information if needed
            if not job.file.fileData:
                file_mgr.retrieve_file_data(job.file)
            # Get the job allowed configuration from the file data
            file_mgr.set_job_allowed_config_from_file_data(job)
            # Get the job estimated needed material per extruder from the file data
            file_mgr.set_job_estimated_needed_material_from_file_data(job)
        except (MissingFileDataKeys, InvalidFileData) as e:
            self.client_namespace.emit_job_analyze_error(job, str(e))
            return
        except DBManagerError:
            self.client_namespace.emit_job_analyze_error(job, "Can't save the retrieved file header at the database")
            return

        self.client_namespace.emit_job_analyze_done(job)
        self.client_namespace.emit_jobs_updated(broadcast=True)

    def enqueue_job(self, job_id: int):
        try:
            job = db_mgr.get_jobs(id=job_id)
        except DBManagerError as e:
            self.client_namespace.emit_job_enqueue_error(None, str(e))
            return

        if job is None:
            self.client_namespace.emit_job_enqueue_error(job, "There is no job with this ID in the database")
            return

        try:
            db_mgr.enqueue_created_job(job)
        except DBManagerError as e:
            self.client_namespace.emit_job_enqueue_error(job, str(e))
            return

        self.client_namespace.emit_job_enqueue_done(job)
        self.client_namespace.emit_jobs_updated(broadcast=True)

        try:
            jobs_in_queue = db_mgr.get_jobs(order_by_priority=True, idState=db_mgr.job_state_ids["Waiting"],
                                            canBePrinted=True)
        except DBManagerError as e:
            self.client_namespace.emit_job_enqueue_error(None, str(e))
            return

        # Get the printer object
        printer = db_mgr.get_printers(id=1)

        if len(jobs_in_queue) == 1 and printer.state.stateString == "Ready":
            self.printer_namespace.emit_print_job(jobs_in_queue[0], broadcast=True)
