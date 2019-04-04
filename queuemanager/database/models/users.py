"""
This module implements the user data related database models.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from ..definitions import db_conn as db
from .table_names import (
    USERS_TABLE
)
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """
    Definition of table USERS_TABLE that contains all users
    """
    __tablename__ = USERS_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    isAdmin = db.Column(db.Boolean, nullable=False, default=False)
    registeredOn = db.Column(db.DateTime, default=datetime.now, nullable=False)

    jobs = db.relationship('Job', back_populates='user', cascade="all, delete-orphan")
    files = db.relationship('File', back_populates='user', cascade="all, delete-orphan")

    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def get_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "isAdmin": self.isAdmin
        }

    def __repr__(self):
        return '[{}]<id: {} / username: {} / isAdmin: {}>'.format(self.__tablename__, self.id,
                                                                  self.username, self.isAdmin)
