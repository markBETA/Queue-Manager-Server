from socketio import Namespace
from flask import current_app, request
from queuemanager.db_manager import DBManagerError, DBInternalError, DBManager
from queuemanager.db_models import PrintSchema
import json



from . import sio

db = DBManager(autocommit=False)

print_schema = PrintSchema()
prints_schema = PrintSchema(many=True)


@sio.on("connect")
def connect():
    current_app.logger.info("client %s connected", request.sid)
    try:
        prints = db.get_prints()
    except DBInternalError:
        return {'message': 'Unable to read the data from the database'}, 500

    sio.emit("queues", json.dumps(prints_schema.dump(prints).data), room=request.sid)


@sio.on("disconnect")
def disconnect():
    current_app.logger.info("client %s disconnected", request.sid)


@sio.on("printer_state_changed")
def printer_state_changed(event, payload):
    current_app.logger.info("printer_state_changed: %s" % payload["state_string"])
    sio.emit("printer_state", payload["state_string"], broadcast=True, include_self=False)
