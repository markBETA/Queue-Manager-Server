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
from ...database import Job, DBManagerError
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
            job = self.db_manager.get_jobs(id=job_id)
        except DBManagerError as e:
            self.client_namespace.emit_job_analyze_error(Job(id=job_id), str(e))
            return

        if job is None:
            self.client_namespace.emit_job_analyze_error(Job(id=job_id), "There is no job with this ID in the app_database")
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
            self.client_namespace.emit_job_analyze_error(job, "Can't save the retrieved file header at the app_database")
            return

        self.client_namespace.emit_job_analyze_done(job)
        self.client_namespace.emit_jobs_updated(broadcast=True)

    def enqueue_job(self, job_id: int):
        try:
            job = self.db_manager.get_jobs(id=job_id)
        except DBManagerError as e:
            self.client_namespace.emit_job_enqueue_error(Job(id=job_id), str(e))
            return

        if job is None:
            self.client_namespace.emit_job_enqueue_error(Job(id=job_id), "There is no job with this ID in the app_database")
            return

        try:
            self.db_manager.enqueue_created_job(job)
        except DBManagerError as e:
            self.client_namespace.emit_job_enqueue_error(job, str(e))
            return

        self.client_namespace.emit_job_enqueue_done(job)
        self.client_namespace.emit_jobs_updated(broadcast=True)

        try:
            jobs_in_queue = self.db_manager.get_jobs(order_by_priority=True,
                                                     idState=self.db_manager.job_state_ids["Waiting"],
                                                     canBePrinted=True)
        except DBManagerError as e:
            self.client_namespace.emit_job_enqueue_error(None, str(e))
            return

        # Get the printer object
        printer = self.db_manager.get_printers(id=1)

        if len(jobs_in_queue) == 1 and printer.state.stateString == "Ready":
            self.assign_job_to_printer(job)
