__author__ = "Eloi Pardo"
__credits__ = ["Eloi Pardo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Eloi Pardo"
__email__ = "epardo@fundaciocim.org"
__status__ = "Development"

import os

from flask import request, json, current_app
from flask_restplus import Resource, Namespace, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename
from queuemanager.db_manager import DBManagerError, DBInternalError, DBManager, UniqueConstraintError
from queuemanager.models.Job import JobSchema
from queuemanager.socket.SocketManager import SocketManager
from queuemanager.utils import GCodeReader

api = Namespace("jobs", description="Jobs related operations")

db = DBManager(autocommit=False)
socket_manager = SocketManager.get_instance()

job_schema = JobSchema()
jobs_schema = JobSchema(many=True)


@api.route("")
class JobList(Resource):
    """
    /jobs
    """
    @api.doc(id="getJobs")
    @api.response(200, "Success")
    @api.response(500, "Unable to read the data from the database")
    def get(self):
        """
        Returns all jobs in the database
        """
        try:
            jobs = db.get_jobs()
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return jobs_schema.dump(jobs).data, 200

    @api.doc(id="postJob")
    @api.response(201, "Success")
    @api.response(400, 'The file format must be "gcode"')
    @api.response(409, "File name already exists")
    @api.response(409, "File path already exists")
    @api.response(409, "Job name already exists")
    @api.response(500, "Unable to write the new entry to the database")
    def post(self):
        """
        Register a new job in the database
        """
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument("name", type=str, required=True, location="form", help="Name cannot be blank!")
        parser.add_argument("gcode", type=FileStorage, required=True, location="files", help="Gcode cannot be blank!")
        args = parser.parse_args()

        job_name = args["name"]
        gcode_file = args["gcode"]
        gcode_name = secure_filename(gcode_file.filename)
        filepath = os.path.join(current_app.config.get('GCODE_STORAGE_PATH'), gcode_name)

        time, filament, extruders = GCodeReader.get_values(gcode_file)
        if gcode_name.rsplit('.', 1)[1].lower() != 'gcode':
            return {'message': 'The file format must be "gcode"'}, 400


        try:
            job = db.insert_job(job_name, gcode_name, filepath, time, filament, extruders)
            db.commit_changes()
        except UniqueConstraintError as e:
            if "files.name" in str(e):
                return {'message': 'File name already exists'}, 409
            elif "files.path" in str(e):
                return {'message': 'File path already exists'}, 409
            elif "jobs.name" in str(e):
                return {'message': 'Job name already exists'}, 409
            else:
                return {'message': str(e)}, 409

        except DBInternalError:
            return {'message': 'Unable to write the new entry to the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400

        # gcode.save(filepath + '.' + str(job.id))
        gcode_file.save(filepath)
        # try:
        #     headers = {'X-Api-Key': 'AAFBCFB524CB4A289B036A434903E47A'}
        #     files = {'file': (gcode_name, gcode, 'application/octet-stream'), 'print': True}
        #     r = requests.post('http://localhost:5000/api/files/sdcard', headers=headers, files=files)
        #     print(r.text)
        # except Exception as e:
        #     return {'message': str(e)}, 400

        socket_manager.send_jobs(**{"broadcast": True})

        return job_schema.dump(job).data, 201


@api.route("/<int:job_id>")
class Job(Resource):
    """
    /jobs/<job_id>
    """
    @api.doc(id="getJob")
    @api.response(200, "Success")
    @api.response(500, "Unable to read the data from the database")
    def get(self, job_id):
        """
        Returns the job with id=job_id
        """
        try:
            job = db.get_job(job_id)
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return job_schema.dump(job).data, 200

    @api.doc("deleteJob")
    @api.response(200, "Success")
    @api.response(500, "Unable to delete from the database")
    def delete(self, job_id):
        """
        Deletes the job with id=job_id
        """
        try:
            job = db.delete_job(job_id)
            if not job:
                return {"message": "Job with id=%d doesn't exist" % job_id}, 404
            filepath = job.file.path
            db.commit_changes()
            os.remove(filepath)
        except DBInternalError:
            return {'message': 'Unable to delete from the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500

        socket_manager.send_jobs(**{"broadcast": True})

        return job_schema.dump(job).data, 200

    @api.doc(id="updateJob")
    @api.response(200, "Success")
    @api.response(400, "No input data provided")
    @api.response(500, "Unable to update the database")
    def put(self, job_id):
        """
        Updates the job with id=job_id
        """
        try:
            json_data = request.get_json(force=True)
        except BadRequest:
            json_data = json.loads(json.dumps(request.form))
        if not json_data:
            return {'message': 'No input data provided'}, 400

        try:
            job = db.update_job(job_id, **json_data)
            if not job:
                return {"message": "Job with id=%d doesn't exist" % job_id}, 404
            db.commit_changes()
        except DBInternalError:
            return {'message': 'Unable to update the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400

        return job_schema.dump(job).data, 200
