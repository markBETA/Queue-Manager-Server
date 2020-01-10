"""
This module implements the socket.io namespaces and the events that the server will be listening for.
Also defines de flask-socketio manager class.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .definitions import socketio, socketio_mgr, client_namespace, printer_namespace
from .manager import SocketIOManager
from .namespaces import ClientNamespace, PrinterNamespace


def init_app(app, *_args, external=False, **kwargs):
    socketio_mgr.set_client_namespace(client_namespace)
    socketio_mgr.set_printer_namespace(printer_namespace)
    socketio_mgr.init_app(app)
    client_namespace.init_app(app)
    printer_namespace.init_app(app)
    if external:
        socketio.init_app(None, **kwargs)
    else:
        socketio.on_namespace(client_namespace)
        socketio.on_namespace(printer_namespace)
        socketio.init_app(app, **kwargs)
