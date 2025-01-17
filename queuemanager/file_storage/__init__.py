"""
This module defines the file storage manager.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .file_manager import FileManager, FileDescriptor

################
# FILE MANAGER #
################

file_mgr = FileManager()


def init_app(app, *args, **kwargs):
    file_mgr.init_app(app, *args, **kwargs)
