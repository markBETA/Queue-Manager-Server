"""
This module implements a high level interface for saving and retrieving data from
the database instance.
"""

__author__ = "Eloi Pardo"
__credits__ = ["Eloi Pardo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Eloi Pardo"
__email__ = "epardo@fundaciocim.org"
__status__ = "Development"


from flask import current_app
from sqlalchemy import exc
from sqlalchemy.orm import exc as ormexc
from queuemanager.db import db
from queuemanager.models.Job import Job
from queuemanager.models.File import File


######################################
# DATABASE MANAGER EXCEPTION CLASSES #
######################################

class DBManagerError(Exception):
    """
    DB Manager Exception upper class.
    """
    pass


class InvalidParameter(DBManagerError):
    """
    This exception represents an invalid parameter input in one of the manager methods.
    """
    pass


class DBInternalError(DBManagerError):
    """
    This exception will be raised when we are unable to write or read from the database
    """
    pass


class UniqueConstraintError(DBManagerError):
    """
    This exception will be raise when the UNIQUE constraint fails
    """
    pass

######################################
# DATABASE MANAGER OBJECT DEFINITION #
######################################

class DBManager(object):
    """
    This class implements the manager for the queuemanager DB
    """

    def __init__(self, autocommit=True):
        self.autocommit = autocommit

    def commit_changes(self):
        # Update the database with error catching
        try:
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(str(e))
            raise UniqueConstraintError(str(e))
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error("Can't update the database. Details: %s", str(e))
            raise DBInternalError("Can't update the database")

    def insert_job(self, name: str, gcode_name: str, filepath: str, time: int, filament: float, extruders):
        if name == "" or filepath == "" or gcode_name == "":
            raise InvalidParameter("The 'name', the 'gcode_name' and 'filepath' parameter can't be an empty string")

        job = Job(name=name)
        file = File(name=gcode_name, path=filepath, time=time, used_extruders=extruders, used_material=filament)
        file.jobs.append(job)

        # Add the print row
        db.session.add(job)
        db.session.add(file)

        # Commit changes to the database
        if self.autocommit:
            self.commit_changes()

        return job

    def get_job(self, job_id):
        # Get the print
        if job_id is not None:
            try:
                job = Job.query.get(job_id)
            except exc.SQLAlchemyError as e:
                current_app.logger.error("Can't retrieve print with id '%s'. Details: %s", job_id, str(e))
                raise DBInternalError("Can't retrieve print with id '{}'".format(job_id))
        else:
            raise InvalidParameter("Job_id can't be None")

        return job

    def get_jobs(self):
        try:
            jobs = Job.query.all()
        except exc.SQLAlchemyError as e:
            current_app.logger.error("Can't retrieve jobs Details: %s", str(e))
            raise DBInternalError("Can't retrieve jobs")

        return jobs

    def delete_job(self, job_id):
        try:
            job = Job.query.get(job_id)
            db.session.delete(job)
        except exc.SQLAlchemyError as e:
            current_app.logger.error("Can't delete the job with id '%s' Details: %s", job_id, str(e))
            raise DBInternalError("Can't delete the job with id '{}'".format(job_id))
        except ormexc.UnmappedInstanceError as e:
            current_app.logger.error("Can't delete the job with id '%s' Details: %s", job_id, str(e))
            raise DBInternalError("Can't delete the job with id '{}'".format(job_id))

        # Commit changes to the database
        if self.autocommit:
            self.commit_changes()

        return job

    def update_job(self, job_id, **kwargs):
        try:
            job = Job.query.get(job_id)
            job.update(**kwargs)
        except exc.SQLAlchemyError as e:
            current_app.logger.error("Can't update the job with id '%s' Details: %s", job_id, str(e))
            raise DBInternalError("Can't update the job with id '{}'".format(job_id))
        except ormexc.UnmappedInstanceError as e:
            current_app.logger.error("Can't update the job with id '%s' Details: %s", job_id, str(e))
            raise DBInternalError("Can't update the job with id '{}'".format(job_id))

        # Commit changes to the database
        if self.autocommit:
            self.commit_changes()

        return job
