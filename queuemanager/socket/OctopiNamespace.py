from flask import current_app, request
from flask_socketio import Namespace

from .SocketManager import SocketManager


class OctopiNamespace(Namespace):

    def __init__(self, namespace=None):
        super().__init__(namespace)
        self._socket_manager = SocketManager.get_instance()

    def on_connect(self):
        current_app.logger.info("client %s connected", request.sid)

    def on_disconnect(self):
        current_app.logger.info("client %s disconnected", request.sid)

    def on_printer_state_changed(self, state):
        current_app.logger.info("printer_state_changed: %s" % state)
        kwargs = {
            "broadcast": True
        }
        self._socket_manager.printer_state = state
        self._socket_manager.send_printer_state(**kwargs)
