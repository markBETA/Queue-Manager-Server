"""
This module implements a high level interface for saving and retrieving data from
the database instance.
"""

__author__ = "Eloi Pardo"
__credits__ = ["Eloi Pardo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Eloi Pardo"
__email__ = "epardo@fundaciocim.org"
__status__ = "Development"

from datetime import datetime, timedelta
from binascii import hexlify
from flask import current_app
from sqlalchemy import exc
from sqlalchemy.orm import aliased
from queuemanager.db_models import db, User, Print
import os


######################################
# DATABASE MANAGER EXCEPTION CLASSES #
######################################

class DBManagerError(Exception):
    """
    DB Manager Exception upper class.
    """
    pass


class InvalidParameter(DBManagerError):
    """
    This exception represents an invalid parameter input in one of the manager methods.
    """
    pass


class InvalidFilterType(DBManagerError):
    """
    This exception represents an invalid filter type input in the get method applied to the finished prints.
    """
    pass


class DBInternalError(DBManagerError):
    """
    This exception will be raised when we are unable to write or read from the database
    """
    pass


######################################
# DATABASE MANAGER OBJECT DEFINITION #
######################################

class DBManager(object):
    """
    This class implements the manager for the queuemanager DB
    """

    def __init__(self, autocommit=True):
        self.autocommit = autocommit

    def commit_changes(self):
        # Update the database with error catching
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error("Can't update the database. Details: %s", str(e))
            raise DBInternalError("Can't update the database")

    def insert_user(self, username: str, password: str, is_admin: bool):
        if username == "":
            raise InvalidParameter("The 'username' parameter can't be an empty string")
        if password == "":
            raise InvalidParameter("The 'password' parameter can't be an empty string")

        user = User(username=username, password=password, is_admin=is_admin)

        # Add the user row
        db.session.add(user)

        # Commit changes to the database
        if self.autocommit:
            self.commit_changes()

        return user

    def get_user(self, user_id=None, username=None):
        # Get the user
        if user_id is not None:
            try:
                user = User.query.get(user_id)
            except exc.SQLAlchemyError as e:
                current_app.logger.error("Can't retrive user with id '%s'. Details: %s", user_id, str(e))
                raise DBInternalError("Can't retrieve user with id '{}'".format(user_id))

        elif username is not None:
            try:
                user = User.query.filter_by(username=username).first()
            except exc.SQLAlchemyError as e:
                current_app.logger.error("Can't retrive user with username '%s'. Details: %s", username, str(e))
                raise DBInternalError("Can't retrieve user with username '{}'".format(username))

        else:
            raise InvalidParameter("Id and username can't be both None")

        return user

    def get_users(self):
        try:
            users = User.query.all()
        except exc.SQLAlchemyError as e:
            current_app.logger.error("Can't retrive users Details: %s", str(e))
            raise DBInternalError("Can't retrieve users")

        return users
