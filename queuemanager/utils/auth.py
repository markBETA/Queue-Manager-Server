import jwt
from functools import wraps
from flask import request
from queuemanager.db_manager import DBManager
from queuemanager.models.User import User

db = DBManager(autocommit=False)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        try:
            user_id = User.decode_auth_token(token)
        except jwt.ExpiredSignatureError:
            return "Token has expired", 401
        except jwt.InvalidTokenError:
            return "Invalid token", 401
        if not token or not user_id:
            return "You have to login with proper credentials", 401
        job_id = kwargs.get("job_id")
        if job_id:
            job = db.get_job(id=job_id)
            if not job:
                return "There is no job with id=%s" % job_id, 401
            if job.user_id != user_id:
                return "Only the user owner can do this", 401
        return f(*args, **kwargs)
    return decorated


def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        try:
            user_id = User.decode_auth_token(token)
        except jwt.ExpiredSignatureError:
            return "Token has expired", 401
        except jwt.InvalidTokenError:
            return "Invalid token", 401
        if not token or not user_id:
            return "You have to login with proper credentials", 401
        user = db.get_user(user_id)
        if not user.is_admin:
            return "You need admin privileges", 401
        return f(*args, **kwargs)
    return decorated
