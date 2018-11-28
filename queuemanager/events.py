from flask import current_app, request
from queuemanager.db_manager import DBManagerError, DBInternalError, DBManager
from queuemanager.db_models import PrintSchema
from queuemanager.socket.SocketManager import SocketManager
import json

socket_manager = SocketManager.get_instance()
sio = socket_manager.sio

print_schema = PrintSchema()
prints_schema = PrintSchema(many=True)


@sio.on("connect")
def connect():
    current_app.logger.info("client %s connected", request.sid)
    socket_manager.send_prints()


@sio.on("disconnect")
def disconnect():
    current_app.logger.info("client %s disconnected", request.sid)


@sio.on("printer_state_changed")
def printer_state_changed(event, payload):
    current_app.logger.info("printer_state_changed: %s" % payload["state_string"])
    sio.emit("printer_state", payload["state_string"], broadcast=True, include_self=False)
