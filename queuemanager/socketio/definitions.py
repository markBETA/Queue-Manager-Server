"""
This module defines the all the global variables needed by the socketio module
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask_socketio import SocketIO

from .manager import SocketIOManager
from .namespaces import ClientNamespace, PrinterNamespace
from .auth import authorize_connection


############################
# SOCKET.IO SERVER MANAGER #
############################

socketio = SocketIO()
socketio_mgr = SocketIOManager()


@socketio.on("connect")
def connected():
    return authorize_connection()


########################
# SOCKET.IO NAMESPACES #
########################

client_namespace = ClientNamespace(socketio, socketio_mgr, "/client")
printer_namespace = PrinterNamespace(socketio, socketio_mgr, "/printer")
