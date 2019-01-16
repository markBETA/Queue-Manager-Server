from flask import current_app, request
from flask_socketio import Namespace, emit

from .SocketManager import SocketManager


class ClientNamespace(Namespace):

    def __init__(self, namespace=None):
        super().__init__(namespace)
        self._socket_manager = SocketManager.get_instance()

    def on_connect(self):
        current_app.logger.info("client %s connected", request.sid)
        kwargs = {
            "room": request.sid
        }
        self._socket_manager.send_queues(**kwargs)
        self._socket_manager.send_printer_state(**kwargs)

    def on_disconnect(self):
        current_app.logger.info("client %s disconnected", request.sid)
