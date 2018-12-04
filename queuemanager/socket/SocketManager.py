from flask_socketio import SocketIO

from queuemanager.db_manager import DBManager, DBInternalError
from queuemanager.db_models import PrintSchema

print_schema = PrintSchema()
prints_schema = PrintSchema(many=True)


class SocketManager:

    def __init__(self):
        super().__init__()
        if SocketManager._instance is not None:
            raise ValueError("Duplicate singleton creation")

        SocketManager._instance = self

        self._printer_state = "Unknown"

        self.sio = SocketIO()
        from .ClientNamespace import ClientNamespace
        from .OctopiNamespace import OctopiNamespace
        self.sio.on_namespace(ClientNamespace("/client"))
        self.sio.on_namespace(OctopiNamespace("/octopi"))

        self._db = DBManager(autocommit=False)

    def init_app(self, app):
        self.sio.init_app(app)

    def send_prints(self, **kwargs):
        try:
            prints = self._db.get_prints()
        except DBInternalError:
            return

        self.sio.emit("queues", prints_schema.jsonify(prints).json, namespace="/client", **kwargs)

    def send_printer_state(self, **kwargs):
        self.sio.emit("printer_state", self.printer_state, namespace="/client", **kwargs)

    @property
    def printer_state(self):
        return self._printer_state

    @printer_state.setter
    def printer_state(self, printer_state):
        self._printer_state = printer_state

    @classmethod
    def get_instance(cls) -> "SocketManager":
        # Note: Explicit use of class name to prevent issues with inheritance.
        if not SocketManager._instance:
            SocketManager._instance = cls()

        return SocketManager._instance

    _instance = None
