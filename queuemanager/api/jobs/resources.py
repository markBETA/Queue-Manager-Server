"""
This module defines the all the api resources for the jobs namespace
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restplus import Resource, marshal
from flask_restplus.mask import apply as apply_mask

from .definitions import api
from .models import (
    job_model, edit_job_model, reorder_job_model, job_state_model
)
from .parameter_schemas import (
    GetJobsSchema, GetJobsNotDoneSchema, DeleteJobSchema
)
from ...database import db_mgr as db
from ...database.manager.exceptions import (
    DBManagerError, UniqueConstraintError
)
from ...file_storage import file_mgr
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
    @api.response(422, "Invalid access token")
    @api.response(500, "Unable to read the data from the database")
    @jwt_required
    def get(self):
        """
        Returns all jobs in the database after apply the filters set in the query
        """
        current_user = get_jwt_identity()

        if current_user.get('type') != "user":
            return {'message': 'Only user access tokens are allowed.'}, 422

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

    @api.doc(id="post_job")
    @api.param("name", "Job name", "formData", **{"type": str, "required": True})
    @api.param("gcode", "Gcode file", "formData", **{"type": "file", "required": True})
    @api.response(201, "Success", job_model)
    @api.response(400, 'No file attached with the request')
    @api.response(400, 'No job name specified with the request')
    @api.response(401, "Unauthorized resource access")
    @api.response(409, "Job name already exists")
    @api.response(422, "Invalid access token")
    @api.response(500, "Unable to save the file")
    @api.response(500, "Unable to write the new job to the database")
    @jwt_required
    def post(self):
        """
        Register a new job in the database
        """
        current_user = get_jwt_identity()

        if current_user.get('type') != "user":
            return {'message': 'Only user access tokens are allowed.'}, 422

        user_id = current_user.get('id')
        if user_id is None:
            return {'message': "Can't retrieve the user ID from the access token."}, 422

        # Check if the post request has the file part
        if 'gcode' not in request.files:
            return {'message': 'No file attached with the request.'}, 400

        # Check if the name of the new job is attached with the form data
        if 'name' not in request.form:
            return {'message': 'No job name specified with the request.'}, 400

        # Get the default user
        user = db.get_users(id=current_user.get('id'))
        if user is None:
            return {'message': "There isn't any registered user with the ID from the access token."}, 422

        # Save the file to the filesystem
        file = file_mgr.save_file(request.files["gcode"], user)

        # Retrieve the file information
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
    @api.param("order_by_priority", "Get the jobs ordered by the priority index", "query", **{"type": bool, "default": False})
    @api.response(200, "Success", [job_model])
    @api.response(400, "Invalid query parameter")
    @api.response(401, "Unauthorized resource access")
    @api.response(422, "Invalid access token")
    @api.response(500, "Unable to read the data from the database")
    @jwt_required
    def get(self):
        """
        Returns all jobs in the database after apply the filters set in the query
        """
        current_user = get_jwt_identity()

        if current_user.get('type') != "user":
            return {'message': 'Only user access tokens are allowed.'}, 422

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
    @api.response(200, "Success", [job_state_model])
    @api.response(401, "Unauthorized resource access")
    @api.response(422, "Invalid access token")
    @api.response(500, "Unable to read the data from the database")
    @jwt_required
    def get(self):
        """
        Returns all the possible job states
        """
        current_user = get_jwt_identity()

        if current_user.get('type') != "user":
            return {'message': 'Only user access tokens are allowed.'}, 422

        job_states = db.get_job_states()

        return marshal(job_states, job_state_model), 200


@api.route("/<int:job_id>")
class Job(Resource):
    """
    /jobs/<job_id>
    """
    @api.doc(id="get_job")
    @api.response(200, "Success", job_model)
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "There is no job with this ID in the database")
    @api.response(422, "Invalid access token")
    @api.response(500, "Unable to read the data from the database")
    @jwt_required
    def get(self, job_id: int):
        """
        Returns the job data with the specified ID
        """
        current_user = get_jwt_identity()

        if current_user.get('type') != "user":
            return {'message': 'Only user access tokens are allowed.'}, 422

        job = db.get_jobs(id=job_id)

        if job is None:
            return {'message': 'There is no job with this ID in the database.'}, 404
        else:
            return marshal(job, job_model, skip_none=True), 200

    @api.doc(id="delete_job")
    @api.param("delete_file", "Delete the file associated with this job", "query", **{"type": bool, "default": True})
    @api.response(200, "Success")
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "There is no job with this ID in the database")
    @api.response(422, "Invalid access token")
    @api.response(500, "Unable to read the data from the database")
    @api.response(500, "Unable to delete the data from the database")
    @api.response(500, "Unable to delete the file from the filesystem")
    @jwt_required
    def delete(self, job_id: int):
        """
        Delete the job with the specified ID
        """
        current_user = get_jwt_identity()

        if current_user.get('type') != "user":
            return {'message': 'Only user access tokens are allowed.'}, 422

        user_id = current_user.get('id')
        if user_id is None:
            return {'message': "Can't retrieve the user ID from the access token."}, 422

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

        if not current_user.get('is_admin') is True and job.idUser != user_id:
            return {'message': "Only admin users can delete a job created by another user."}, 401

        if delete_file:
            file_mgr.delete_file(job.file)
        else:
            db.delete_job(job)

        socketio_mgr.client_namespace.emit_jobs_updated(broadcast=True)

        return {'message': 'Job <{}> deleted from the database.'.format(job.name)}, 200

    @api.doc(id="put_job")
    @api.expect(edit_job_model, validate=True)
    @api.response(200, "Success", job_model)
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "There is no job with this ID in the database")
    @api.response(422, "Invalid access token")
    @api.response(500, "Unable to read the data from the database")
    @api.response(500, "Unable to edit the job from the database")
    @jwt_required
    def put(self, job_id: int):
        """
        Edit the job with the specified ID
        """
        # Delete the unwanted keys from the Json payload
        payload = apply_mask(request.json, edit_job_model, skip=True)

        current_user = get_jwt_identity()

        if current_user.get('type') != "user":
            return {'message': 'Only user access tokens are allowed.'}, 422

        user_id = current_user.get('id')
        if user_id is None:
            return {'message': "Can't retrieve the user ID from the access token."}, 422

        job = db.get_jobs(id=job_id)

        if job is None:
            return {'message': 'There is no job with this ID in the database.'}, 404

        if not current_user.get('is_admin') is True and job.idUser != user_id:
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
    @api.expect(reorder_job_model, validate=True)
    @api.response(200, "Job reordered successfully")
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "There is no job with this ID in the database")
    @api.response(422, "Invalid access token")
    @api.response(500, "Unable to read the data from the database")
    @api.response(500, "Unable to edit the job from the database")
    @jwt_required
    def put(self, job_id: int):
        current_user = get_jwt_identity()

        if current_user.get('type') != "user":
            return {'message': 'Only user access tokens are allowed.'}, 422

        if not current_user.get('is_admin') is True:
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
