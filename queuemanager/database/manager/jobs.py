"""
This module contains the database manager class for the file operations.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from sqlalchemy.orm import scoped_session

from .base_class import DBManagerBase
from .exceptions import (
    InvalidParameter
)
from ..models import (
    Job, JobState, JobAllowedMaterial, JobAllowedExtruder, User, File, PrinterMaterial,
    PrinterExtruderType, PrinterState, Printer
)


class DBManagerJobStates(DBManagerBase):
    """
    This class implements the database manager class for the job states operations
    """
    def get_job_states(self, **kwargs):
        # Create the query object
        query = JobState.query

        # Filter by the given kwargs
        for key, value in kwargs.items():
            if hasattr(JobState, key):
                query = query.filter_by(**{key: value})
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Return all the filtered items
        if len(kwargs) > 0:
            return self.execute_query(query, use_list=False)
        else:
            return self.execute_query(query)


class DBManagerJobAllowedMaterials(DBManagerBase):
    """
    This class implements the database manager class for the job states operations
    """
    def insert_job_allowed_materials(self, job: Job, allowed_materials: list, add_to_database: bool = True):
        # Initialize the JobAllowedMaterial objects list
        job_allowed_materials = []

        # Create the allowed materials relations
        for material, extruder_index in allowed_materials:
            # Check that the members of the allowed_materials array are PrinterMaterial objects
            if not isinstance(material, PrinterMaterial):
                raise InvalidParameter("The elements of the 'allowed_materials' parameter needs to be "
                                       "PrinterMaterial objects")
            # Create the JobAllowedMaterial object
            job_allowed_material = JobAllowedMaterial(
                idJob=job.id,
                idMaterial=material.id,
                extruderIndex=extruder_index
            )
            # Add the object to the database (if specified)
            if add_to_database:
                self.add_row(job_allowed_material)
            # Add the object to the allowed materials list
            job_allowed_materials.append(job_allowed_material)

        # Set the job allowed materials
        job.allowed_materials = job_allowed_materials

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return job_allowed_materials

    def get_job_allowed_materials(self, job: Job, extruder_index: int = None):
        # Create the query object
        query = JobAllowedMaterial.query.filter_by(idJob=job.id)

        if extruder_index is not None:
            # Get all the allowed materials of the job by the extruder index
            query = query.filter_by(extruderIndex=extruder_index)

        # Initialize the materials array
        printer_materials = []
        # Populate it
        for job_allowed_material in self.execute_query(query):
            printer_materials.append(job_allowed_material.material)

        return printer_materials

    def get_jobs_by_material(self, material: PrinterMaterial, extruder_index: int = None):
        # Create the query object
        query = JobAllowedMaterial.query.filter_by(idMaterial=material.id)

        if extruder_index is not None:
            # Get all the allowed materials of the job by the extruder index
            query = query.filter_by(extruderIndex=extruder_index)

        # Initialize the jobs array
        jobs = []
        # Populate it
        for job_allowed_material in self.execute_query(query):
            jobs.append(job_allowed_material.job)

        return jobs


class DBManagerJobAllowedExtruderTypes(DBManagerBase):
    """
    This class implements the database manager class for the job states operations
    """
    def insert_job_allowed_extruder_types(self, job: Job, allowed_extruder_types: list, add_to_database: bool = True):
        # Initialize the JobAllowedExtruderTypes objects list
        job_allowed_extruders = []

        # Create the allowed extruder types relations
        for extruder_type, extruder_index in allowed_extruder_types:
            # Check that the members of the allowed_extruder_types array are PrinterExtruderType objects
            if not isinstance(extruder_type, PrinterExtruderType):
                raise InvalidParameter("The elements of the 'allowed_extruder_types' parameter needs to be "
                                       "PrinterExtruderType objects")
            # Create the JobAllowedExtruder object
            job_allowed_extruder = JobAllowedExtruder(
                idJob=job.id,
                idExtruderType=extruder_type.id,
                extruderIndex=extruder_index
            )
            # Add the object to the database (if specified)
            if add_to_database:
                self.add_row(job_allowed_extruder)
            # Add the object to the allowed extruder types list
            job_allowed_extruders.append(job_allowed_extruder)

        # Set the job allowed extruders objects
        job.allowed_extruder_types = job_allowed_extruders

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return job_allowed_extruders

    def get_job_allowed_extruder_types(self, job: Job, extruder_index: int = None):
        # Create the query object
        query = JobAllowedExtruder.query.filter_by(idJob=job.id)

        if extruder_index is not None:
            # Get all the allowed materials of the job by the extruder index
            query = query.filter_by(extruderIndex=extruder_index)

        # Initialize the extruder types array
        printer_extruder_types = []
        # Populate it
        for job_allowed_extruder in self.execute_query(query):
            printer_extruder_types.append(job_allowed_extruder.type)

        return printer_extruder_types

    def get_jobs_by_extruder_type(self, extruder_type: PrinterExtruderType, extruder_index: int = None):
        # Create the query object
        query = JobAllowedExtruder.query.filter_by(idExtruderType=extruder_type.id)

        if extruder_index is not None:
            # Get all the allowed materials of the job by the extruder index
            query = query.filter_by(extruderIndex=extruder_index)

        # Initialize the jobs array
        jobs = []
        # Populate it
        for job_allowed_extruder in self.execute_query(query):
            jobs.append(job_allowed_extruder.job)

        return jobs


class DBManagerJobs(DBManagerJobStates, DBManagerJobAllowedMaterials, DBManagerJobAllowedExtruderTypes):
    """
    This class implements the database manager class for the file operations
    """
    def __init__(self, autocommit: bool = True, override_session: scoped_session = None):
        super().__init__(autocommit, override_session)
        self._job_initial_state = None
        self._job_waiting_state = None
        self._job_printing_state = None
        self._job_finished_state = None
        self._job_done_state = None

    def init_static_values(self):
        # Save the job states in memory (for avoid consulting it each time)
        self._job_initial_state = self.get_job_states(stateString="Created")
        self._job_waiting_state = self.get_job_states(stateString="Waiting")
        self._job_printing_state = self.get_job_states(stateString="Printing")
        self._job_finished_state = self.get_job_states(stateString="Finished")
        self._job_done_state = self.get_job_states(stateString="Done")

    def _check_can_be_printed_job(self, job: Job):
        # Get all the working printers
        query = Printer.query.join(PrinterState).filter(PrinterState.isOperationalState.is_(True))
        working_printers = self.execute_query(query)
        # Initialize the usable printers array
        usable_printers = [True] * len(working_printers)

        # Iterate over the printer extruders of all the working printers
        for i in range(len(working_printers)):
            printer = working_printers[i]
            for extruder in printer.extruders:
                # Get the allowed materials for this extruder index
                allowed_materials = self.get_job_allowed_materials(job, extruder_index=extruder.index)
                # Check that the actual extruder material is in the allowed materials array
                if allowed_materials and extruder.material not in allowed_materials:
                    usable_printers[i] = False
                    break
                # Get the allowed extruder types for this extruder index
                allowed_extruder_types = self.get_job_allowed_extruder_types(job, extruder_index=extruder.index)
                # Check that the actual extruder material is in the allowed materials array
                if allowed_extruder_types and extruder.type not in allowed_extruder_types:
                    usable_printers[i] = False
                    break

        # Return True if any of the working printers is usable for this job
        return any(usable_printers)

    def insert_job(self, name: str, file: File, user: User):
        # Check parameter values
        if name == "":
            raise InvalidParameter("The 'name' parameter can't be an empty string")

        # Create the new job object
        job = Job(
            name=name,
            idState=self._job_initial_state.id,
            idFile=file.id,
            idUser=user.id
        )

        # Add the new row to the database (including child objects)
        self.add_row(job)

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return job

    def get_jobs(self, order_by_priority: bool = False, **kwargs):
        # Create the query object
        if order_by_priority:
            query = Job.query.order_by(Job.priority_i.asc())
        else:
            query = Job.query

        # Filter by the given kwargs
        for key, value in kwargs.items():
            if hasattr(Job, key):
                if key in ("id", "name"):
                    return self.execute_query(query.filter_by(**{key: value}), use_list=False)
                else:
                    query = query.filter_by(**{key: value})
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Return all the filtered items
        return self.execute_query(query)

    def update_job(self, job: Job, **kwargs):
        # Modify the specified job fields
        for key, value in kwargs.items():
            if hasattr(Job, key):
                setattr(job, key, value)
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return job

    def update_can_be_printed_jobs(self):
        # Get all the jobs in waiting state
        jobs = self.execute_query(Job.query.filter_by(idState=self._job_waiting_state.id))

        # Disable the autocommit (if enabled)
        self._set_autocommit(False)

        # Recheck if can be printer for all the working jobs
        for job in jobs:
            can_be_printed = self._check_can_be_printed_job(job)
            self.update_job(job, canBePrinted=can_be_printed)

        # Restore the autocommit initial value
        self._restore_autocommit()

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

    def enqueue_created_job(self, job: Job):
        # Check that the job is in the initial state
        if job.state.id != self._job_initial_state.id:
            raise InvalidParameter("The job to enqueue needs to be in the initial state ('Created')")

        # Check if the job can be printed with the actual printer configuration
        can_be_printed = self._check_can_be_printed_job(job)

        # Get the job with the lowest priority
        query = Job.query.filter(Job.priority_i.isnot(None)).order_by(Job.priority_i.desc())
        lowest_priority_job = self.execute_query(query, use_list=False)

        # If there is no jobs in the queue already (no jobs with assigned priority_i), give the
        # priority index 1 to this job
        job_priority_i = 1 if lowest_priority_job is None else lowest_priority_job.priority_i + 1

        # Update the job priority_i, state and if can be printed
        self.update_job(job, priority_i=job_priority_i, state=self._job_waiting_state, canBePrinted=can_be_printed)

        return job

    def get_first_job_in_queue(self):
        # Get head of the jobs queue
        query = Job.query.filter_by(idState=self._job_waiting_state.id).filter_by(canBePrinted=True).\
            order_by(Job.priority_i.asc())

        return self.execute_query(query, use_list=False)

    def set_printing_job(self, job: Job):
        # First check if the job can be printed and is in waiting state
        if not job.canBePrinted or job.state != self._job_waiting_state:
            raise InvalidParameter("This job can't be printed with any printer")

        # Update the job state to printing and erase the priority_i of the job
        self.update_job(job, idState=self._job_printing_state.id, priority_i=None)

        return job

    def set_finished_job(self, job: Job):
        # First check if the job was in 'Printing' state
        if job.state != self._job_printing_state:
            raise InvalidParameter("The job needs to be in 'Printing' state to change to 'Finished' state")

        # Update the job state to printing and erase the priority_i of the job
        self.update_job(job, idState=self._job_finished_state.id)

        return job

    def set_done_job(self, job: Job):
        # First check if the job was in 'Finished' state
        if job.state != self._job_finished_state:
            raise InvalidParameter("The job needs to be in 'Finished' state to change to 'Done' state")

        # Update the job state to printing and erase the priority_i of the job
        self.update_job(job, idState=self._job_done_state.id)

        return job

    def reorder_job_in_queue(self, job: Job, after: Job):
        # Check that the job is in waiting state
        if job.state != self._job_waiting_state:
            raise InvalidParameter("The job to reorder needs to be in the 'Waiting' state")

        # Create the query object
        query = Job.query.filter(Job.priority_i.isnot(None))

        # If the after job is None, that means that the new job position will be the first in the queue
        if after is None:
            # Get the job with the lowest priority_i
            highest_priority_job = self.execute_query(query.order_by(Job.priority_i.asc()), use_list=False)
            # Update the job priority_i, state and if can be printed
            self.update_job(job, priority_i=highest_priority_job.priority_i - 1)
            # Return the modified job
            return job
        # Check that the after job is in waiting state also
        elif after.state != self._job_waiting_state:
            raise InvalidParameter("The job to put after needs to be in the 'Waiting' state")

        original_priority_i = job.priority_i

        # Algorithm if the 'after' job priority index is lower than the original one
        if after.priority_i < original_priority_i:
            # In this case, the new priority will be the one after the 'after' job
            job.priority_i = after.priority_i + 1
            # Update all the jobs between
            query = query.filter(Job.priority_i > after.priority_i).\
                filter(Job.priority_i < original_priority_i)
            self.execute_update(query, {Job.priority_i: Job.priority_i + 1})
        # Algorithm if the 'after' job priority index is higher than the original one
        elif after.priority_i > original_priority_i:
            # In this case, the new priority will be the 'after' job's priority
            job.priority_i = after.priority_i
            # Get all the jobs between
            query = query.filter(Job.priority_i <= after.priority_i). \
                filter(Job.priority_i > original_priority_i)
            self.execute_update(query, {Job.priority_i: Job.priority_i - 1})
        else:
            return

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

    def enqueue_printing_or_finished_job(self, job: Job, max_priority: bool):
        # Check that the job is in the printing or finished state
        if job.state not in (self._job_printing_state, self._job_finished_state):
            raise InvalidParameter("The job to enqueue needs to be in the  state ('Created')")

        # Check if the job can be printed with the actual printer configuration
        can_be_printed = self._check_can_be_printed_job(job)

        query = Job.query.filter(Job.priority_i.isnot(None))

        if max_priority:
            # Get the job with the lowest priority_i
            highest_priority_job = self.execute_query(query.order_by(Job.priority_i.asc()), use_list=False)
            job_priority_i = 1 if highest_priority_job is None else highest_priority_job.priority_i - 1
        else:
            # Get the job with the highest priority_i
            lowest_priority_job = self.execute_query(query.order_by(Job.priority_i.desc()), use_list=False)
            job_priority_i = 1 if lowest_priority_job is None else lowest_priority_job.priority_i + 1

        # Update the job priority_i, state and if can be printed
        self.update_job(job, priority_i=job_priority_i, state=self._job_waiting_state, canBePrinted=can_be_printed)

        return job
