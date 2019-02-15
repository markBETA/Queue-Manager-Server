from flask import make_response, jsonify
from flask_restplus import Resource, Namespace, reqparse
from queuemanager.db_manager import DBManagerError, DBInternalError, DBManager, UniqueConstraintError

api = Namespace("users", description="Authentication related operations")

db = DBManager(autocommit=False)


@api.route("")
class User(Resource):

    @api.doc(id="postUser")
    @api.param("username", "Username", "formData", **{"type": str, "required": True})
    @api.param("password", "Password", "formData", **{"type": str, "required": True})
    @api.response(201, "Success")
    @api.response(409, "User already exists")
    @api.response(500, "Unable to write the new entry to the database")
    def post(self):
        """
        Register a new job in the database
        """
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument("username", type=str, required=True, location="form", help="Username cannot be blank!")
        parser.add_argument("password", type=str, required=True, location="form", help="Password cannot be blank!")
        args = parser.parse_args()

        username = args["username"]
        password = args["password"]

        try:
            user = db.insert_user(username, password)
            db.commit_changes()
            # generate the auth token
            auth_token = user.encode_auth_token(user.id)
            response = {
                'status': 'success',
                'message': 'Successfully registered.',
                'auth_token': auth_token.decode()
            }
            return make_response(jsonify(response)), 201

        except UniqueConstraintError as e:
            return {'message': str(e)}, 409

        except DBInternalError:
            return {'message': 'Unable to write the new entry to the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400
