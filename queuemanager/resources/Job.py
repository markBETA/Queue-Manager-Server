__author__ = "Eloi Pardo"
__credits__ = ["Eloi Pardo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Eloi Pardo"
__email__ = "epardo@fundaciocim.org"
__status__ = "Development"

import os

from flask_restful import Resource
from flask import request, json, current_app
from werkzeug.exceptions import BadRequest
from queuemanager.db_manager import DBManagerError, DBInternalError, DBManager, UniqueConstraintError
from queuemanager.models.Job import JobSchema
from queuemanager.socket.SocketManager import SocketManager


db = DBManager()
socket_manager = SocketManager.get_instance()

job_schema = JobSchema()
jobs_schema = JobSchema(many=True)


class JobList(Resource):
    """
    /jobs
    """

    def get(self):
        """
        Returns all jobs in the database
        """
        try:
            prints = db.get_jobs()
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return jobs_schema.dump(prints).data, 200

    def post(self):
        """
        Register a new job in the database
        """
        try:
            json_data = request.get_json(force=True)
        except BadRequest:
            json_data = json.loads(json.dumps(request.form))
        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Check that the retrieved data has all parameters
        if not {"name"}.issubset(json_data.keys()):
            return {'message': 'Missing JSON keys'}, 400

        # Iterate over data received keys for checking that there are correct
        for key in json_data:
            if key != "name" and type(json_data[key]) != str:
                return {'message': "Invalid parameter '" + key + "'"}, 400

        gcode = request.files.get('gcode')
        gcode_name = gcode.filename
        if gcode_name.rsplit('.', 1)[1].lower() != 'gcode':
            return {'message': 'The file format must be "gcode"'}, 400

        filepath = os.path.join(current_app.config.get('GCODE_STORAGE_PATH'), gcode_name)


        try:
            job = db.insert_job(json_data['name'], filepath)
            db.commit_changes()
        except UniqueConstraintError:
            return {'message': 'Print name is not unique'}, 409
        except DBInternalError:
            return {'message': 'Unable to write the new entry to the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400

        gcode.save(filepath + '.' + str(job.id))
        # try:
        #     headers = {'X-Api-Key': 'AAFBCFB524CB4A289B036A434903E47A'}
        #     files = {'file': (gcode_name, gcode, 'application/octet-stream'), 'print': True}
        #     r = requests.post('http://localhost:5000/api/files/sdcard', headers=headers, files=files)
        #     print(r.text)
        # except Exception as e:
        #     return {'message': str(e)}, 400

        socket_manager.send_jobs(**{"broadcast": True})

        return job_schema.dump(job).data, 201


class Job(Resource):
    """
    /jobs/<job_id>
    """

    def get(self, job_id):
        """
        Returns the job with id==job_id
        """
        try:
            job = db.get_job(job_id)
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return job_schema.dump(job).data, 200

    def delete(self, job_id):
        """
        Deletes the job with id==job_id
        """
        try:
            job = db.delete_job(job_id)
            db.commit_changes()
        except DBInternalError:
            return {'message': 'Unable to delete from the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400

        os.remove(job.filepath + '.' + job_id)

        socket_manager.send_jobs(**{"broadcast": True})

        return job_schema.dump(job).data, 200

    def put(self, job_id):
        """
        Updates the job with id==job_id
        """
        try:
            json_data = request.get_json(force=True)
        except BadRequest:
            json_data = json.loads(json.dumps(request.form))
        if not json_data:
            return {'message': 'No input data provided'}, 400

        try:
            job = db.update_job(job_id, **json_data)
        except DBInternalError:
            return {'message': 'Unable to delete from the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400

        return job_schema.dump(job).data, 200
