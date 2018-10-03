__author__ = "Eloi Pardo"
__credits__ = ["Eloi Pardo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Eloi Pardo"
__email__ = "epardo@fundaciocim.org"
__status__ = "Development"

from flask_restful import Resource
from flask import request
from werkzeug.exceptions import BadRequest
from queuemanager.db_manager import DBManagerError, DBInternalError, DBManager
from queuemanager.db_models import UserSchema

db = DBManager(autocommit=False)

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class UserList(Resource):
    """
    /users
    """

    def get(self):
        """
        Returns all users int the database
        """
        try:
            user = db.get_users()
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return users_schema.dump(user).data, 200

    def post(self):
        """
        Register a new user in the database
        """
        try:
            json_data = request.get_json(force=True)
        except BadRequest:
            return {'message': 'Incorrect JSON format'}, 400
        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Check that the retrieved data has all parameters
        if not {"username", "password", "is_admin"}.issubset(json_data.keys()):
            return {'message': 'Missing JSON keys'}, 400

        # Iterate over data received keys for checking that there are correct
        for key in json_data:
            if type(json_data[key]) != str:
                return {'message': "Invalid parameter '" + key + "'"}, 400
            if key == "is_admin":
                if json_data[key].lower() == "false":
                    json_data[key] = False
                elif json_data[key].lower() == "true":
                    json_data[key] = True
                else:
                    return {'message': "Invalid parameter '" + key + "'"}, 400

        # Check that there isn't any user with that username
        try:
            user = db.get_user(username=json_data["username"])
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500
        if user is not None:
            return user_schema.dump(user).data, 409

        try:
            user = db.insert_user(username=json_data["username"], password=json_data["password"], is_admin=json_data["is_admin"])
            db.commit_changes()
        except DBInternalError:
            return {'message': 'Unable to write the new entry to the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400

        return user_schema.dump(user).data, 201


class User(Resource):
    """
    /users/<user_id>
    """

    def get(self, user_id):
        """
        Returns the user with id==user_id
        """
        try:
            user = db.get_user(user_id=user_id)
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return user_schema.dump(user).data, 200
