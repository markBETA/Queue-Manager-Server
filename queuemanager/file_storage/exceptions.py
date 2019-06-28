"""
This module contains the file manager exception classes.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.2"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"


class FileManagerError(Exception):
    """
    File Manager Exception upper class.
    """
    pass


class InvalidFileType(FileManagerError):
    """
    This exception represents an invalid type of a file.
    """
    pass


class InvalidFileData(FileManagerError):
    """
    This exception represents an invalid information fields of a file.
    """
    pass


class MissingFileDataKeys(FileManagerError):
    """
    This exception represents when one or more keys of the header are missing
    """
    pass


class FilesystemError(FileManagerError):
    """
    This exception represents when there was an error accessing to the filesystem
    """
    pass
