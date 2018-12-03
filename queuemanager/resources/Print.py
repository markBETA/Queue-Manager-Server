__author__ = "Eloi Pardo"
__credits__ = ["Eloi Pardo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Eloi Pardo"
__email__ = "epardo@fundaciocim.org"
__status__ = "Development"

import os
import requests

from flask_restful import Resource
from flask import request, json, current_app
from werkzeug.exceptions import BadRequest
from queuemanager.db_manager import DBManagerError, DBInternalError, DBManager, UniqueConstraintError
from queuemanager.db_models import PrintSchema
from queuemanager.socket.SocketManager import SocketManager
from sqlalchemy.exc import IntegrityError

db = DBManager(autocommit=False)
socket_manager = SocketManager.get_instance()

print_schema = PrintSchema()
prints_schema = PrintSchema(many=True)


class PrintList(Resource):
    """
    /prints
    """

    def get(self):
        """
        Returns all prints in the database
        """
        try:
            prints = db.get_prints()
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return prints_schema.dump(prints).data, 200

    def post(self):
        """
        Register a new print in the database
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
            print_ = db.insert_print(json_data['name'], filepath)
            db.commit_changes()
        except UniqueConstraintError:
            return {'message': 'Print name is not unique'}, 409
        except DBInternalError:
            return {'message': 'Unable to write the new entry to the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400

        gcode.save(filepath + '.' + str(print_.id))
        # try:
        #     headers = {'X-Api-Key': 'AAFBCFB524CB4A289B036A434903E47A'}
        #     files = {'file': (gcode_name, gcode, 'application/octet-stream'), 'print': True}
        #     r = requests.post('http://localhost:5000/api/files/sdcard', headers=headers, files=files)
        #     print(r.text)
        # except Exception as e:
        #     return {'message': str(e)}, 400

        socket_manager.send_prints(**{"broadcast": True})

        return print_schema.dump(print_).data, 201


class Print(Resource):
    """
    /prints/<print_id>
    """

    def get(self, print_id):
        """
        Returns the print with id==print_id
        """
        try:
            print_ = db.get_print(print_id)
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return print_schema.dump(print_).data, 200

    def delete(self, print_id):
        """
        Deletes the print with id==print_id
        """
        try:
            print_ = db.delete_print(print_id)
            db.commit_changes()
        except DBInternalError:
            return {'message': 'Unable to delete from the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400

        os.remove(print_.filepath + '.' + print_id)

        socket_manager.send_prints(**{"broadcast": True})

        return print_schema.dump(print_).data, 202
