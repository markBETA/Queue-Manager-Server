"""
This module contains the database manager base class.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"


class SocketIOManagerBase(object):
    """
    This class implements the database manager base class
    """

    def __init__(self):
        self.client_namespace = None
        self.printer_namespace = None

    def set_client_namespace(self, client_namespace):
        self.client_namespace = client_namespace

    def set_printer_namespace(self, printer_namespace):
        self.printer_namespace = printer_namespace
