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

    def on_printer_state_changed(self, event, payload):
        current_app.logger.info("printer_state_changed: %s" % payload["state_string"])
        kwargs = {
            "broadcast": True
        }
        self._socket_manager.printer_state = payload["state_string"]
        self._socket_manager.send_printer_state(**kwargs)
