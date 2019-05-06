"""
This module contains the database manager class for the file operations.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .base_class import DBManagerBase
from .exceptions import (
    InvalidParameter
)
from ..models import (
    User, File
)


class DBManagerFiles(DBManagerBase):
    """
    This class implements the database manager class for the file operations
    """
    def insert_file(self, user: User, name: str, full_path: str = None, **kwargs):
        # Check parameter values
        if name == "":
            raise InvalidParameter("The 'name' parameter can't be an empty string")
        if full_path == "":
            raise InvalidParameter("The 'full_path' parameter can't be an empty string")

        # Create the new file object
        file = File(
            idUser=user.id,
            name=name,
            fullPath=full_path,
        )

        # Add the optional values to the file object
        for key, value in kwargs.items():
            if hasattr(File, key):
                setattr(file, key, value)
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Link the user with the file
        file.user = user

        # Add the new row to the database
        self.add_row(file)

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return file

    def get_files(self, **kwargs):
        # Create the query object
        query = File.query

        # Filter by the given kwargs
        for key, value in kwargs.items():
            if hasattr(File, key):
                if key in ("id", "fullPath"):
                    return self.execute_query(query.filter_by(**{key: value}), use_list=False)
                else:
                    query = query.filter_by(**{key: value})
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Return all the filtered items
        return self.execute_query(query)

    def update_file(self, file: File, **kwargs):
        # Modify the specified file fields
        for key, value in kwargs.items():
            if hasattr(File, key):
                setattr(file, key, value)
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return file

    def delete_files(self, **kwargs):
        # Initialize the deleted files counter
        deleted_files_count = 0

        # Get all the files with this parameters
        files = self.get_files(**kwargs)

        # Check the type of data that we obtained from the last call
        if files is None:
            return deleted_files_count
        elif isinstance(files, File):
            # Delete the retrieved file
            self.del_row(files)
            deleted_files_count = 1
        else:
            # Delete all the retrieved files
            for file in files:
                self.del_row(file)
                deleted_files_count += 1

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return deleted_files_count
