from flask_restplus import Resource, Namespace, reqparse
from queuemanager.db_manager import DBManagerError, DBInternalError, DBManager, UniqueConstraintError
from queuemanager.models.User import UserSchema
from queuemanager.utils import auth

api = Namespace("users", description="Authentication related operations")

db = DBManager(autocommit=False)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

header_parser = api.parser()
header_parser.add_argument("Authorization", type=str, required=True, location="headers", help="Token needed")


@api.route("")
class UserList(Resource):
    """
    /users
    """
    @api.doc(id="getUsers")
    @api.expect(header_parser)
    @api.response(200, "Success")
    @api.response(500, "Unable to read the data from the database")
    @auth.requires_admin
    def get(self):
        """
        Returns all users in the database
        """
        try:
            users = db.get_users()
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return users_schema.dump(users).data, 200

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
            return user_schema.dump(user).data, 201

        except UniqueConstraintError as e:
            if "users.username" in str(e):
                return {'message': 'Username already exists'}, 409
            return {'message': str(e)}, 409
        except DBInternalError:
            return {'message': 'Unable to write the new entry to the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400


@api.route("/<int:user_id>")
class User(Resource):
    """
    /users/<user_id>
    """
    @api.doc(id="getUser")
    @api.response(200, "Success")
    @api.response(404, "User with id=user_id doesn't exist")
    @api.response(500, "Unable to read the data from the database")
    def get(self, user_id):
        """
        Returns the user with id=user_id
        """
        try:
            user = db.get_job(user_id)
            if not user:
                return {"message": "Job with id=%d doesn't exist" % user_id}, 404
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return user_schema.dump(user).data, 200

    @api.doc(id="updateUser")
    @api.expect(header_parser)
    @api.param("username", "Username", "formData", **{"type": str, "example": "seat"})
    @api.param("password", "Password", "formData", **{"type": str, "example": "xxxx"})
    @api.param("is_admin", "Is user admin?", "formData", **{"type": bool, "example": True})
    @api.response(200, "Success")
    @api.response(400, "No input data provided")
    @api.response(404, "User with id=user_id doesn't exist")
    @api.response(500, "Unable to update the database")
    @auth.requires_admin
    def put(self, user_id):
        """
        Updates the user with id=user_id
        """
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument("username", type=str, location="form", store_missing=False)
        parser.add_argument("password", type=str, location="form", store_missing=False)
        parser.add_argument("is_admin", type=bool, location="form", store_missing=False)
        args = parser.parse_args()

        if not bool(args):
            return {'message': 'No input data provided'}, 400

        try:
            user = db.update_user(user_id, **args)
            if not user:
                return {"message": "User with id=%d doesn't exist" % user_id}, 404
            db.commit_changes()
        except DBInternalError:
            return {'message': 'Unable to update the database'}, 500
        except DBManagerError as e:
            return {'message': str(e)}, 400

        return user_schema.dump(user).data, 200


@api.route("/login")
class LoginUser(Resource):
    """
    /users/login
    """
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
