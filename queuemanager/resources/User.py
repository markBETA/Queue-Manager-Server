from flask_restplus import Resource, Namespace, reqparse
from queuemanager.db_manager import DBManagerError, DBInternalError, DBManager, UniqueConstraintError

api = Namespace("users", description="Authentication related operations")

db = DBManager(autocommit=False)


@api.route("/register")
class RegisterUser(Resource):

    @api.doc(id="register")
    @api.param("username", "Username", "formData", **{"type": str, "required": True})
    @api.param("password", "Password", "formData", **{"type": str, "required": True})
    @api.response(201, "Success")
    @api.response(409, "Username already exists")
    @api.response(500, "Unable to write the new entry to the database")
    def post(self):
        """
        Register a new user in the database
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
            response = {
                'status': 'success',
                'message': 'Successfully registered.'
            }
            return response, 201

        except UniqueConstraintError as e:
            if "users.username" in str(e):
                return {'message': 'Username already exists'}, 409
            return {'message': str(e)}, 409
        except DBInternalError:
            return {'message': 'Unable to write the new entry to the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400


@api.route("/login")
class LoginUser(Resource):

    @api.doc(id="login")
    @api.param("username", "Username", "formData", **{"type": str, "required": True})
    @api.param("password", "Password", "formData", **{"type": str, "required": True})
    @api.response(201, "Success")
    @api.response(500, "Unable to write the new entry to the database")
    def post(self):
        """
        Login
        """
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument("username", type=str, required=True, location="form", help="Username cannot be blank!")
        parser.add_argument("password", type=str, required=True, location="form", help="Password cannot be blank!")
        args = parser.parse_args()

        username = args["username"]
        password = args["password"]

        try:
            user = db.get_user_by_username(username)
            if not user or not user.verify_password(password):
                return {"message": "Invalid username or password!"}, 400
            # generate the auth token
            auth_token = user.encode_auth_token(user.id)
            response = {
                'status': 'success',
                'message': 'Successfully logged in.',
                'auth_token': auth_token.decode()
            }
            return response, 201

        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500
