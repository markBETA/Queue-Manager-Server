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

from flask import request, current_app
from flask_restplus import Resource, marshal

from .definitions import api
from .models import (
    job_model
)
from ..definitions import prepare_database_filters
from ...database import db_mgr as db
from ...database.manager.exceptions import (
    DBInternalError, DBManagerError, UniqueConstraintError
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
    @api.param("id_file", "Get job(s) with this file ID", "query", **{"type": int})
    @api.param("id_user", "Get job(s) created by this user ID", "query", **{"type": int})
    @api.param("name", "Get job with this name", "query", **{"type": str})
    @api.param("can_be_printed", "Get jobs that can be printed or not", "query", **{"type": bool})
    @api.param("order_by_priority", "Get the jobs ordered by the priority index", "query", **{"type": bool})
    @api.response(200, "Success", [job_model])
    @api.response(400, "Invalid query parameter")
    @api.response(500, "Unable to read the data from the database")
    def get(self):
        """
        Returns all jobs in the database after apply the filters set in the query
        """
        allowed_filters = {"id", "state", "id_file", "id_user", "name", "can_be_printed", "order_by_priority"}

        try:
            database_filters = prepare_database_filters(request.args, allowed_filters=allowed_filters)
        except KeyError as e:
            return {'message': str(e)}, 400

        # Get the job state object from the state string set in the query
        if "state" in database_filters:
            try:
                database_filters["idState"] = db.job_state_ids[database_filters["state"]]
                del database_filters["state"]
            except KeyError:
                return {'message': 'Unknown state string'}, 400

        # Read the 'order_by_priority' param from the query
        order_by_priority = False
        if "order_by_priority" in request.args:
            order_by_priority = request.args["order_by_priority"]
            del database_filters["orderByPriority"]

        try:
            jobs = db.get_jobs(order_by_priority, **database_filters)
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400

        return marshal(jobs, job_model, skip_none=True), 200

    @api.doc(id="post_job")
    @api.param("name", "Job name", "formData", **{"type": str, "required": True})
    @api.param("gcode", "Gcode file", "formData", **{"type": "file", "required": True})
    @api.response(201, "Success", job_model)
    @api.response(400, 'No file attached with the request')
    @api.response(400, 'No job name specified with the request')
    @api.response(409, "Job name already exists")
    @api.response(500, "Unable to save the file")
    @api.response(500, "Unable to write the new job to the database")
    def post(self):
        """
        Register a new job in the database
        """
        # Check if the post request has the file part
        if 'gcode' not in request.files:
            return {'message': 'No file attached with the request'}, 400

        # Check if the name of the new job is attached with the form data
        if 'name' not in request.form:
            return {'message': 'No job name specified with the request'}, 400

        # Get the default user # TODO Change this with the user from the session data!
        default_user = db.get_users(id=1)

        # Save the file to the filesystem
        try:
            file = file_mgr.save_file(request.files["gcode"], default_user)
        except (FileManagerError, DBManagerError) as e:
            return {'message': str(e)}, 500

        # Retrieve the file information
        try:
            file_mgr.retrieve_file_basic_info(file)
        except (FileManagerError, DBManagerError):
            current_app.logger.warning("Can't retrieve the file '{}' information".format(file))

        # Create the job from the file
        try:
            job = db.insert_job(request.form["name"], file, default_user)
        except DBManagerError as e:
            try:
                file_mgr.delete_file(file)
            except (FileManagerError, DBManagerError):
                pass
            if isinstance(e, UniqueConstraintError):
                return {'message': 'Job name already exists'}, 409
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
    @api.param("order_by_priority", "Get the jobs ordered by the priority index", "query", **{"type": bool})
    @api.response(200, "Success", [job_model])
    @api.response(400, "Invalid query parameter")
    @api.response(500, "Unable to read the data from the database")
    def get(self):
        """
        Returns all jobs in the database after apply the filters set in the query
        """
        allowed_filters = {"order_by_priority"}

        try:
            prepare_database_filters(request.args, allowed_filters=allowed_filters)
        except KeyError as e:
            return {'message': str(e)}, 400

        # Read the 'order_by_priority' param from the query
        order_by_priority = False
        if "order_by_priority" in request.args:
            order_by_priority = request.args["order_by_priority"]

        try:
            jobs = db.get_not_done_jobs(order_by_priority)
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400

        return marshal(jobs, job_model, skip_none=True), 200
#
#
# @api.route("/<int:job_id>")
# class Job(Resource):
#     """
#     /jobs/<job_id>
#     """
#     @api.doc(id="getJob")
#     @api.response(200, "Success")
#     @api.response(404, "Job with id=job_id doesn't exist")
#     @api.response(500, "Unable to read the data from the database")
#     def get(self, job_id):
#         """
#         Returns the job with id=job_id
#         """
#         try:
#             job = db.get_job(id=job_id)
#             if not job:
#                 return {"message": "Job with id=%d doesn't exist" % job_id}, 404
#         except DBInternalError:
#             return {'message': 'Unable to read the data from the database'}, 500
#
#         return job_schema.dump(job).data, 200
#
#     @api.doc("deleteJob")
#     @api.expect(header_parser)
#     @api.response(200, "Success")
#     @api.response(404, "Job with id=job_id doesn't exist")
#     @api.response(500, "Unable to delete from the database")
#     @auth.requires_auth
#     def delete(self, job_id):
#         """
#         Deletes the job with id=job_id
#         """
#         try:
#             job = db.delete_job(job_id)
#             if not job:
#                 return {"message": "Job with id=%d doesn't exist" % job_id}, 404
#             filepath = job.file.path
#             response = job_schema.dump(job).data
#             db.commit_changes()
#             os.remove(filepath)
#         except DBInternalError:
#             return {'message': 'Unable to delete from the database'}, 500
#         except DBManagerError as e:
#             return {'message': str(e)}, 400
#         except Exception as e:
#             return {'message': str(e)}, 500
#
#         socket_manager.send_queues(**{"broadcast": True})
#
#         return response, 200
#
#     @api.doc(id="updateJob")
#     @api.expect(header_parser)
#     @api.param("name", "Job name", "formData", **{"type": str, "example": "benchy"})
#     @api.param("order", "Order", "formData", **{"type": int, "example": 3})
#     @api.response(200, "Success")
#     @api.response(400, "No input data provided")
#     @api.response(404, "Job with id=job_id doesn't exist")
#     @api.response(500, "Unable to update the database")
#     @auth.requires_admin
#     def put(self, job_id):
#         """
#         Updates the job with id=job_id
#         """
#         parser = reqparse.RequestParser(bundle_errors=True)
#         parser.add_argument("name", type=str, location="form", store_missing=False)
#         parser.add_argument("order", type=int, location="form", store_missing=False)
#         args = parser.parse_args()
#
#         if not bool(args):
#             return {'message': 'No input data provided'}, 400
#
#         try:
#             job = db.update_job(job_id, **args)
#             if not job:
#                 return {"message": "Job with id=%d doesn't exist" % job_id}, 404
#             db.commit_changes()
#         except DBInternalError:
#             return {'message': 'Unable to update the database'}, 500
#         except DBManagerError as e:
#             return {'message': str(e)}, 400
#
#         socket_manager.send_queues(**{"broadcast": True})
#
#         return job_schema.dump(job).data, 200
