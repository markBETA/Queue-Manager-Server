"""
This module implements the socket.io namespaces and the events that the server will be listening for.
Also defines de flask-socketio manager class.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .definitions import socketio
from .namespaces import client_namespace

socketio.on_namespace(client_namespace)
