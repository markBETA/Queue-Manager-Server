"""
This module contains the socketio_printer manager class.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"


from .client import ClientNamespaceManager
from .printer import PrinterNamespaceManager


class SocketIOManager(ClientNamespaceManager, PrinterNamespaceManager):
    def __init__(self):
        super(ClientNamespaceManager, self).__init__()
        super(PrinterNamespaceManager, self).__init__()
