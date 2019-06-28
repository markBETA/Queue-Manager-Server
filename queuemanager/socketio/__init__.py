"""
This module implements the socket.io namespaces and the events that the server will be listening for.
Also defines de flask-socketio manager class.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.2"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .definitions import socketio, socketio_mgr
from .manager import SocketIOManager
from .namespaces import ClientNamespace, PrinterNamespace

client_namespace = ClientNamespace(socketio_mgr, "/client")
printer_namespace = PrinterNamespace(socketio_mgr, "/printer")
socketio_mgr.set_client_namespace(client_namespace)
socketio_mgr.set_printer_namespace(printer_namespace)
socketio.on_namespace(client_namespace)
socketio.on_namespace(printer_namespace)


def init_app(app, *args, **kwargs):
    socketio.init_app(app, *args, **kwargs)
    client_namespace.init_app(app)
    printer_namespace.init_app(app)
    socketio_mgr.init_app(app)
