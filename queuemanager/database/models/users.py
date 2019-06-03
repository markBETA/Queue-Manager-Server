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

from datetime import datetime

from .table_names import (
    USERS_TABLE
)
from ..definitions import db_conn as db, bind_key


class User(db.Model):
    """
    Definition of table USERS_TABLE that contains all users
    """
    __bind_key__ = bind_key
    __tablename__ = USERS_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(256), unique=True, nullable=False)
    fullname = db.Column(db.String(256))
    email = db.Column(db.String(256), unique=True, nullable=False)
    registeredOn = db.Column(db.DateTime, default=datetime.now, nullable=False)

    jobs = db.relationship('Job', back_populates='user', cascade="all, delete-orphan")
    files = db.relationship('File', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return '[{}]<id: {} / username: {} / email: {}>'.format(self.__tablename__, self.id,
                                                                self.username, self.email)
