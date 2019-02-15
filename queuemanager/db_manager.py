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
from queuemanager.models.Queue import Queue
from queuemanager.models.Extruder import Extruder
from queuemanager.models.User import User


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

    # Job Operations

    def insert_job(self, name: str, gcode_name: str, filepath: str, time: int, filament: float, extruders):
        if name == "" or filepath == "" or gcode_name == "":
            raise InvalidParameter("The 'name', the 'gcode_name' and 'filepath' parameter can't be an empty string")

        job = Job(name=name)
        file = File(name=gcode_name, path=filepath, time=time, used_material=filament)
        job.file = file
        queue = Queue.query.filter_by(active=True).first()
        if extruders:
            for key, value in extruders.items():
                extruder = Extruder.query.filter_by(index=key, nozzle_diameter=value).first()
                if extruder:
                    file.used_extruders.append(extruder)

            for extruder in file.used_extruders:
                if not extruder in queue.used_extruders:
                    waiting_queue = Queue.query.filter_by(active=False).first()
                    waiting_queue.jobs.append(job)
                    break
            else:
                queue.jobs.append(job)
        else:
            queue.jobs.append(job)

        # Add the print row
        db.session.add(file)
        db.session.add(job)
        db.session.add(queue)

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
            if not job:
                return None
            db.session.delete(job.file)
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
            if not job:
                return None
            job.update_helper(**kwargs)
        except exc.SQLAlchemyError as e:
            current_app.logger.error("Can't update the job with id '%s' Details: %s", job_id, str(e))
            raise DBInternalError("Can't update the job with id '{}'".format(job_id))
        except ormexc.UnmappedInstanceError as e:
            current_app.logger.error("Can.'t update the job with id '%s' Details: %s", job_id, str(e))
            raise DBInternalError("Can't update the job with id '{}'".format(job_id))

        # Commit changes to the database
        if self.autocommit:
            self.commit_changes()

        return job

    # Queue operations

    def get_queue_by_id(self, queue_id):
        # Get the print
        if queue_id is not None:
            try:
                queue = Queue.query.get(queue_id)
            except exc.SQLAlchemyError as e:
                current_app.logger.error("Can't retrieve queue with id '%s'. Details: %s", queue_id, str(e))
                raise DBInternalError("Can't retrieve queue with id '{}'".format(queue_id))
        else:
            raise InvalidParameter("Queue id can't be None")

        return queue

    def get_queues(self):
        try:
            queues = Queue.query.all()
        except exc.SQLAlchemyError as e:
            current_app.logger.error("Can't retrieve queues Details: %s", str(e))
            raise DBInternalError("Can't retrieve queues")

        return queues

    def get_queue(self, active):
        try:
            queue = Queue.query.filter_by(active=active).first()
        except exc.SQLAlchemyError as e:
            current_app.logger.error("Can't retrieve queue Details: %s", str(e))
            raise DBInternalError("Can't retrieve queue")

        return queue

    def update_queue(self, printer_info):
        queue = Queue.query.filter_by(name="active").first()
        if not queue.used_extruders:
            for key, value in printer_info.items():
                extruder = Extruder.query.filter_by(index=key, nozzle_diameter=value).first()
                queue.used_extruders.append(extruder)

        else:
            new_used_extruders = []
            for key, value in printer_info.items():
                new_used_extruders.append(Extruder.query.filter_by(index=key, nozzle_diameter=value).first())
            queue.used_extruders = new_used_extruders

        if self.autocommit:
            self.commit_changes()

    def insert_user(self, username, password):
        user = User(username=username)
        user.hash_password(password)

        # Add the user row
        db.session.add(user)

        # Commit changes to the database
        if self.autocommit:
            self.commit_changes()

        return user
