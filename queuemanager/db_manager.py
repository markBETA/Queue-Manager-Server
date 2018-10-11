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


from flask import current_app
from sqlalchemy import exc
from sqlalchemy.orm import exc as ormexc
from queuemanager.db_models import db, Print


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

    def insert_print(self, name: str, filepath):
        if name == "" or filepath == "":
            raise InvalidParameter("The 'name' and the 'filepath' parameter can't be an empty string")

        print_ = Print(name, filepath)

        # Add the print row
        db.session.add(print_)

        # Commit changes to the database
        if self.autocommit:
            self.commit_changes()

        return print_

    def get_print(self, print_id):
        # Get the print
        if print_id is not None:
            try:
                _print = Print.query.get(print_id)
            except exc.SQLAlchemyError as e:
                current_app.logger.error("Can't retrieve print with id '%s'. Details: %s", print_id, str(e))
                raise DBInternalError("Can't retrieve print with id '{}'".format(print_id))
        else:
            raise InvalidParameter("Print_id can't be None")

        return _print

    def get_prints(self):
        try:
            prints = Print.query.all()
        except exc.SQLAlchemyError as e:
            current_app.logger.error("Can't retrieve prints Details: %s", str(e))
            raise DBInternalError("Can't retrieve prints")

        return prints

    def delete_print(self, print_id):
        try:
            print_ = Print.query.get(print_id)
            db.session.delete(print_)
        except exc.SQLAlchemyError as e:
            current_app.logger.error("Can't delete the print with id '%s' Details: %s", print_id, str(e))
            raise DBInternalError("Can't delete the print with id '{}'".format(print_id))
        except ormexc.UnmappedInstanceError as e:
            current_app.logger.error("Can't delete the print with id '%s' Details: %s", print_id, str(e))
            raise DBInternalError("Can't delete the print with id '{}'".format(print_id))

        # Commit changes to the database
        if self.autocommit:
            self.commit_changes()

        return print_
