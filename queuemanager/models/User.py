import jwt
from datetime import datetime, timedelta
from marshmallow import fields
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash
from queuemanager.db import db
from flask import current_app

ma = Marshmallow()


class User(db.Model):
    """
    Definition of the table users that contains all users
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    registered_on = db.Column(db.DateTime, default=datetime.now, nullable=False)
    jobs = db.relationship("Job", backref="user")

    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def encode_auth_token(user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.now() + timedelta(days=0, seconds=5),
                'iat': datetime.now(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class UserSchema(ma.Schema):
    id = fields.Integer()
    username = fields.String()
    admin = fields.Boolean()
    registered_on = fields.DateTime('%d-%m-%YT%H:%M:%S')
