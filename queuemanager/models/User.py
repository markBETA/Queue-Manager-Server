import jwt
from datetime import datetime, timedelta
from marshmallow import fields
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.event import listens_for
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

    def update_helper(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

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
                'exp': datetime.utcnow() + timedelta(days=0, hours=5),
                'iat': datetime.utcnow(),
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
        payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
        return payload['sub']


@listens_for(User.__table__, "after_create")
def insert_initial_values(*args, **kwargs):
    db.session.add(User(username="admin", password=generate_password_hash("1234"), admin=True))
    db.session.commit()


class UserSchema(ma.Schema):
    id = fields.Integer()
    username = fields.String()
    admin = fields.Boolean()
    registered_on = fields.DateTime('%d-%m-%YT%H:%M:%S')
