"""
This module defines the all the API resources for the jobs namespace.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask import request, current_app
from flask_restplus import Resource, marshal
from flask_restplus.mask import apply as apply_mask

from .definitions import api
from .models import (
    job_model, edit_job_model, reorder_job_model, job_state_model
)
from .parameter_schemas import (
    GetJobsSchema, GetJobsNotDoneSchema, DeleteJobSchema
)
from ...identity import identity_mgr
from ...database import db_mgr as db
from ...database.manager.exceptions import (
    DBManagerError, UniqueConstraintError
)
from ...file_storage import FileDescriptor, file_mgr
from ...file_storage.exceptions import (
    FileManagerError
)
from ...socketio import socketio_mgr


@api.route("")
class Jobs(Resource):
    """
    /jobs
    """
    @api.doc(id="get_jobs")
    @api.doc(security="user_identity")
    @api.param("id", "Get job with this ID", "query", **{"type": int})
    @api.param("state", "Get job(s) with this state", "query", **{"type": str})
    @api.param("file_id", "Get job(s) with this file ID", "query", **{"type": int})
    @api.param("user_id", "Get job(s) created by this user ID", "query", **{"type": int})
    @api.param("name", "Get job with this name", "query", **{"type": str})
    @api.param("can_be_printed", "Get jobs that can be printed or not", "query", **{"type": bool})
    @api.param("order_by_priority", "Get the jobs ordered by the priority index", "query", **{"type": bool, "default": False})
    @api.response(200, "Success", [job_model])
    @api.response(400, "Invalid query parameter")
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "The requested job don\'t exist")
    @api.response(422, "Invalid identity")
    @api.response(500, "Unable to read the data from the database")
    @identity_mgr.identity_required()
    def get(self):
        """
        Returns all jobs in the database after apply the filters set in the query
        """
        current_user = identity_mgr.get_identity()

        if current_user['type'] != "user":
            return {'message': 'Only users are allowed to this API resource.'}, 422

        deserialized_parameters = GetJobsSchema().load(request.args)

        if deserialized_parameters.errors:
            return {
                "errors": deserialized_parameters.errors,
                "message": "Query parameters validation failed."
            }, 400
        else:
            deserialized_parameters = deserialized_parameters.data

        # Read the 'order_by_priority' param from the query
        order_by_priority = deserialized_parameters["order_by_priority"]
        del deserialized_parameters["order_by_priority"]

        jobs = db.get_jobs(order_by_priority, **deserialized_parameters)

        if jobs is not None:
            return marshal(jobs, job_model, skip_none=True), 200
        else:
            return {'message': 'The requested job don\'t exist.'}, 404


@api.route("/create")
class JobCreate(Resource):
    @staticmethod
    def _generate_file_descriptor_production():
        # Read the file name and temporary path from the request form data
        filename = request.form["gcode.name"]
        tmp_path = request.form["gcode.path"]

        return FileDescriptor(filename, path=tmp_path)

    @staticmethod
    def _generate_file_descriptor_development():
        # Get the file name and the flask file object from the request files
        flask_file = request.files["gcode"]
        filename = flask_file.filename

        return FileDescriptor(filename, flask_file_obj=flask_file)

    @api.doc(id="create_job")
    @api.doc(security="user_identity")
    @api.param("name", "Job name", "formData", **{"type": str, "required": True})
    @api.param("gcode", "Gcode file", "formData", **{"type": "file", "required": True})
    @api.response(201, "Success")
    @api.response(400, 'No file attached with the request')
    @api.response(400, 'No job name specified with the request')
    @api.response(401, "Unauthorized resource access")
    @api.response(409, "Job name already exists")
    @api.response(422, "Invalid identity")
    @api.response(500, "Unable to save the file")
    @api.response(500, "Unable to write the new job to the database")
    @identity_mgr.identity_required(force_auth_subrequest=current_app.config.get("ENV") == "production")
    def post(self):
        """
        Create a new job using the GCODE located at the request body or the server filesystem
        (depends on the environment)
        """
        current_user = identity_mgr.get_identity()

        if current_user['type'] != "user":
            return {'message': 'Only users are allowed to this API resource.'}, 422

        # Check if the name of the new job is attached with the form data
        if 'name' not in request.form:
            return {'message': 'No job name specified with the request.'}, 400

        # Get the user from the user ID
        user = db.get_users(id=current_user['id'])
        if user is None:
            return {'message': "There isn't any registered user with the ID from the access token."}, 422

        if current_app.config.get("ENV") == "production":
            file_descriptor = self._generate_file_descriptor_production()
        else:
            # Check if the post request has the file part
            if 'gcode' not in request.files:
                return {'message': 'No file attached with the request.'}, 400
            file_descriptor = self._generate_file_descriptor_development()

        # Save the file into the server files storage
        file = file_mgr.save_file(file_descriptor, user)
        file_mgr.retrieve_file_basic_info(file)

        # Create the job from the file
        try:
            job = db.insert_job(request.form["name"], file, user)
        except DBManagerError as e:
            try:
                file_mgr.delete_file(file)
            except (FileManagerError, DBManagerError):
                pass
            if isinstance(e, UniqueConstraintError):
                return {'message': 'Job name already exists.'}, 409
            else:
                return {'message': str(e)}, 500

        socketio_mgr.client_namespace.emit_jobs_updated(broadcast=True)

        return marshal(job, job_model, skip_none=True), 201


@api.route("/not_done")
class NotDoneJobs(Resource):
    """
    /jobs/not_done
    """
    @api.doc(id="get_not_done_jobs")
    @api.doc(security="user_identity")
    @api.param("order_by_priority", "Get the jobs ordered by the priority index", "query", **{"type": bool, "default": False})
    @api.response(200, "Success", [job_model])
    @api.response(400, "Invalid query parameter")
    @api.response(401, "Unauthorized resource access")
    @api.response(422, "Invalid identity")
    @api.response(500, "Unable to read the data from the database")
    @identity_mgr.identity_required()
    def get(self):
        """
        Returns all the not done jobs in the database after apply the filters set in the query
        """
        current_user = identity_mgr.get_identity()

        if current_user['type'] != "user":
            return {'message': 'Only users are allowed to this API resource.'}, 422

        deserialized_parameters = GetJobsNotDoneSchema().load(request.args)

        if deserialized_parameters.errors:
            return {
                       "errors": deserialized_parameters.errors,
                       "message": "Query parameters validation failed."
                   }, 400
        else:
            deserialized_parameters = deserialized_parameters.data

        jobs = db.get_not_done_jobs(deserialized_parameters["order_by_priority"])

        return marshal(jobs, job_model, skip_none=True), 200


@api.route("/states")
class JobStates(Resource):
    """
    /jobs/states
    """
    @api.doc(id="get_jobs_states")
    @api.doc(security="user_identity")
    @api.response(200, "Success", [job_state_model])
    @api.response(401, "Unauthorized resource access")
    @api.response(422, "Invalid identity")
    @api.response(500, "Unable to read the data from the database")
    @identity_mgr.identity_required()
    def get(self):
        """
        Returns all the possible job states
        """
        current_user = identity_mgr.get_identity()

        if current_user['type'] != "user":
            return {'message': 'Only users are allowed to this API resource.'}, 422

        job_states = db.get_job_states()

        return marshal(job_states, job_state_model), 200


@api.route("/<int:job_id>")
class Job(Resource):
    """
    /jobs/<job_id>
    """
    @api.doc(id="get_job")
    @api.doc(security="user_identity")
    @api.response(200, "Success", job_model)
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "There is no job with this ID in the database")
    @api.response(422, "Invalid identity")
    @api.response(500, "Unable to read the data from the database")
    @identity_mgr.identity_required()
    def get(self, job_id: int):
        """
        Returns the job data with the specified ID
        """
        current_user = identity_mgr.get_identity()

        if current_user['type'] != "user":
            return {'message': 'Only users are allowed to this API resource.'}, 422

        job = db.get_jobs(id=job_id)

        if job is None:
            return {'message': 'There is no job with this ID in the database.'}, 404
        else:
            return marshal(job, job_model, skip_none=True), 200

    @api.doc(id="delete_job")
    @api.doc(security="user_identity")
    @api.param("delete_file", "Delete the file associated with this job", "query", **{"type": bool, "default": True})
    @api.response(200, "Success")
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "There is no job with this ID in the database")
    @api.response(422, "Invalid identity")
    @api.response(500, "Unable to read the data from the database")
    @api.response(500, "Unable to delete the data from the database")
    @api.response(500, "Unable to delete the file from the filesystem")
    @identity_mgr.identity_required()
    def delete(self, job_id: int):
        """
        Delete the job with the specified ID
        """
        current_user = identity_mgr.get_identity()

        if current_user['type'] != "user":
            return {'message': 'Only users are allowed to this API resource.'}, 422

        deserialized_parameters = DeleteJobSchema().load(request.args)

        if deserialized_parameters.errors:
            return {
                       "errors": deserialized_parameters.errors,
                       "message": "Query parameters validation failed."
                   }, 400
        else:
            delete_file = deserialized_parameters.data["delete_file"]

        job = db.get_jobs(id=job_id)

        if job is None:
            return {'message': 'There is no job with this ID in the database.'}, 404

        if not current_user.get('is_admin') is True and job.idUser != current_user['id']:
            return {'message': "Only admin users can delete a job created by another user."}, 401

        if delete_file:
            file_mgr.delete_file(job.file)
        else:
            db.delete_job(job)

        socketio_mgr.client_namespace.emit_jobs_updated(broadcast=True)

        return {'message': 'Job <{}> deleted from the database.'.format(job.name)}, 200

    @api.doc(id="put_job")
    @api.doc(security="user_identity")
    @api.expect(edit_job_model, validate=True)
    @api.response(200, "Success", job_model)
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "There is no job with this ID in the database")
    @api.response(422, "Invalid identity")
    @api.response(500, "Unable to read the data from the database")
    @api.response(500, "Unable to edit the job from the database")
    @identity_mgr.identity_required()
    def put(self, job_id: int):
        """
        Edit the job with the specified ID
        """
        # Delete the unwanted keys from the Json payload
        payload = apply_mask(request.json, edit_job_model, skip=True)

        current_user = identity_mgr.get_identity()

        if current_user['type'] != "user":
            return {'message': 'Only users are allowed to this API resource.'}, 422

        job = db.get_jobs(id=job_id)

        if job is None:
            return {'message': 'There is no job with this ID in the database.'}, 404

        if not current_user.get('is_admin') is True and job.idUser != current_user['id']:
            return {'message': "Only admin users can delete a job created by another user."}, 401

        try:
            updated_job = db.update_job(job, **payload)
        except UniqueConstraintError:
            return {'message': 'Job name already exists.'}, 409

        socketio_mgr.client_namespace.emit_jobs_updated(broadcast=True)

        return marshal(updated_job, job_model, skip_none=True), 200


@api.route("/<int:job_id>/reorder")
class JobReorder(Resource):
    """
    /jobs/<int:job_id>/reorder
    """
    @api.doc(id="reorder_job")
    @api.doc(security="user_identity")
    @api.expect(reorder_job_model, validate=True)
    @api.response(200, "Job reordered successfully")
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "There is no job with this ID in the database")
    @api.response(422, "Invalid identity")
    @api.response(500, "Unable to read the data from the database")
    @api.response(500, "Unable to edit the job from the database")
    @identity_mgr.identity_required()
    def put(self, job_id: int):
        """
        Reorder the specified job
        """
        current_user = identity_mgr.get_identity()

        if current_user['type'] != "user":
            return {'message': 'Only users are allowed to this API resource.'}, 422

        if not current_user['is_admin'] is True:
            return {'message': "Only admin users can reorder jobs."}, 401

        previous_job_id = request.json.get("previous_job_id")
        if previous_job_id is not None and previous_job_id < 0:
            previous_job_id = None

        job = db.get_jobs(id=job_id)

        if job is None:
            return {'message': 'There is no job with this ID in the database.'}, 404

        if previous_job_id is not None:
            previous_job = db.get_jobs(id=previous_job_id)
            if previous_job is None:
                return {'message': 'There is no job with this ID in the database.'}, 404
        else:
            previous_job = None

        db.reorder_job_in_queue(job, previous_job)

        socketio_mgr.client_namespace.emit_jobs_updated(broadcast=True)

        return {'message': 'Job <{}> reordered successfully.'.format(job.name)}, 200


@api.route("/<int:job_id>/reprint")
class JobReprint(Resource):
    """
    /jobs/<int:job_id>/reprint
    """
    @api.doc(id="reprint_job")
    @api.doc(security="user_identity")
    @api.response(200, "Job enqueued for reprint successfully")
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "There is no job with this ID in the database")
    @api.response(422, "Invalid identity")
    @api.response(500, "Unable to read the data from the database")
    @api.response(500, "Unable to edit the job from the database")
    @identity_mgr.identity_required()
    def put(self, job_id: int):
        """
        Reprint a job that is in 'Done' state
        """
        current_user = identity_mgr.get_identity()

        if current_user.get('type') != "user":
            return {'message': 'Only users are allowed to this API resource.'}, 422

        job = db.get_jobs(id=job_id)

        if job is None:
            return {'message': 'There is no job with this ID in the database.'}, 404

        db.reprint_done_job(job)

        socketio_mgr.client_namespace.emit_jobs_updated(broadcast=True)

        jobs_in_queue = db.count_jobs_in_queue(only_can_be_printed=True)

        if jobs_in_queue == 1:
            socketio_mgr.assign_job_to_printer(job)

        return {'message': 'Job <{}> enqueued for reprint.'.format(job.name)}, 200
