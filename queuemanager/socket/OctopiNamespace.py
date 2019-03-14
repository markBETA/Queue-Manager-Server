import requests
from flask import current_app, request
from flask_socketio import Namespace
from queuemanager.db_manager import DBManager, DBInternalError
from .SocketManager import SocketManager

db = DBManager()


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

        # TODO handle all states and jobs sent to octoprint

        if state == "Operational" and not db.is_job_printing():
            send_job()
        elif state == "Finishing":
            db.delete_printing_job()
            send_job()
        elif state == "Cancelling":
            job = db.get_job(printing=True)
            if job:
                db.update_job(job.id, **{"printing": False})

    def on_printer_info(self, printer_info):
        try:
            if printer_info is not None:
                db.update_queue(printer_info)
        except DBInternalError:
            return


def send_job():
    try:
        job = db.get_next_job()
        if job:
            gcode_name = job.file.name
            with open(job.file.path) as gcode:
                headers = {'X-Api-Key': current_app.config.get("OCTOPI_API_KEY")}
                files = {'file': (gcode_name, gcode, 'application/octet-stream')}
                body = {"print": True}
                r = requests.post('http://localhost:5000/api/files/local', headers=headers, files=files, data=body)
                print(r.text)
                db.update_job(job.id, **{"printing": True})
    except DBInternalError:
        return
