"""
This module contains the database manager class for the user operations.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .base_class import DBManagerBase
from ..models import (
    User, File
)
from .exceptions import (
    InvalidParameter
)


class DBManagerUsers(DBManagerBase):
    """
    This class implements the database manager class for the user operations
    """
    def insert_user(self, username: str, password: str, is_admin: bool = False):
        # Check parameter values
        if username == "":
            raise InvalidParameter("The 'username' parameter can't be an empty string")
        if password == "":
            raise InvalidParameter("The 'password' parameter can't be an empty string")

        # Create the new user object
        user = User(
            username=username,
            isAdmin=is_admin,
        )

        # Hash the password and save the value
        user.hash_password(password)

        # Add the new row to the database
        self.add_row(user)

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return user

    def get_users(self, **kwargs):
        # Create the query object
        query = User.query

        # Filter by the given kwargs
        for key, value in kwargs.items():
            if hasattr(User, key):
                if key in ("id", "username"):
                    return self.execute_query(query.filter_by(**{key: value}), use_list=False)
                else:
                    query = query.filter_by(**{key: value})
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Return all the filtered items
        return self.execute_query(query)

    def delete_users(self, **kwargs):
        # Initialize the deleted users counter
        deleted_users_count = 0

        # Get all the users with this parameters
        users = self.get_users(**kwargs)

        # Check the type of data that we obtained from the last call
        if users is None:
            return deleted_users_count
        elif isinstance(users, User):
            # Delete the retrieved user
            self.del_row(users)
            deleted_users_count = 1
        else:
            # Delete all the retrieved users
            for user in users:
                self.del_row(user)
                deleted_users_count += 1

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return deleted_users_count
