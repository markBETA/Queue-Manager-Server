from flask import current_app, request
from flask_socketio import Namespace, emit

from .SocketManager import SocketManager


class QueueManagerNamespace(Namespace):

    def __init__(self):
        super().__init__()
        self._socket_manager = SocketManager.get_instance()

    def on_connect(self):
        current_app.logger.info("client %s connected", request.sid)
        self._socket_manager.send_prints()

    def on_disconnect(self):
        current_app.logger.info("client %s disconnected", request.sid)

    def on_printer_state_changed(self, event, payload):
        current_app.logger.info("printer_state_changed: %s" % payload["state_string"])
        emit("printer_state", payload["state_string"], broadcast=True, include_self=False)

