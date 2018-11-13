from socketio import Namespace
from flask import current_app, request

from . import sio


@sio.on("connect")
def connect():
    current_app.logger.info("client %s connected", request.sid)


@sio.on("disconnect")
def disconnect():
    current_app.logger.info("client %s disconnected", request.sid)


@sio.on("printer_state_changed")
def printer_state_changed(payload):
    current_app.logger.info("printer_state_changed", payload)
