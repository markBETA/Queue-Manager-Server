"""
This module defines the all the global variables needed by the jobs namespace
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from ...file_storage import FileManager, file_mgr
from ...file_storage.exceptions import InvalidFileHeader, MissingHeaderKeys
from ...database import DBManager, db_mgr
from ...database import File, Job, DBManagerError
from ...socketio import socketio
# from queuemanager import create_app
# import os


# def update_job_allowed_configuration(file_mgr: FileManager, job: Job):
def update_job_allowed_configuration(job: Job):
    # Get the job allowed configuration from the file header
    file_mgr.set_job_allowed_config_from_header(job)


# def enqueue_job(db_mgr: DBManager, job: Job):
def enqueue_job(job: Job):
    # Enqueue the job
    db_mgr.enqueue_created_job(job)


def analise_file(original_path, file: File, job: Job = None):
    # os.chdir(original_path)

    # Initialize the app context
    # app = create_app(__name__)

    # with app.app_context():
        # Create the new scoped_session
        # options = dict(bind=db.engine, binds={})
        # session = db.create_scoped_session(options=options)

        # db_mgr = DBManager()

        # Initialize the DB manager
        # db_mgr.set_session_object()
        # db_mgr.init_static_values()

        # Create the file manager object
        # file_mgr = FileManager(db_mgr, app)

    # Extract the file header from the file content
    try:
        file_mgr.retrieve_file_header(file)
    except DBManagerError:
        socketio.emit("job_analysis_error", "Can't save the retrieved file header at the database.",
                      namespace='/client')

    # Extract the file information from the file header
    try:
        file_mgr.set_file_information_from_header(file)
    except (MissingHeaderKeys, InvalidFileHeader) as e:
        socketio.emit("job_analysis_error", str(e), namespace='/client')
        return
    except DBManagerError:
        socketio.emit("job_analysis_error", "Can't save the retrieved file information at the database.",
                      namespace='/client')
        return

    # Update the job allowed configuration and enqueue it (if job is not None)
    if job is not None:
        try:
            update_job_allowed_configuration(job)
            enqueue_job(job)
        except (MissingHeaderKeys, InvalidFileHeader) as e:
            socketio.emit("job_analysis_error", str(e), namespace='/client')
        except DBManagerError:
            socketio.emit("job_analysis_error", "Can't save the job updates at the database.", namespace='/client')

        socketio.emit("jobs_updated", namespace='/client')
