"""
This module defines the file storage manager
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .file_manager import FileManager
from ..database import db_mgr

################
# FILE MANAGER #
################

file_mgr = FileManager(db_mgr)
