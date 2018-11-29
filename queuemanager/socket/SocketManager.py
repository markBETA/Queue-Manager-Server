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

        self.sio = SocketIO()
        from .QueueManagerNamespace import QueueManagerNamespace
        self.sio.on_namespace(QueueManagerNamespace())

        self._db = DBManager(autocommit=False)

    def init_app(self, app):
        self.sio.init_app(app)

    def send_prints(self):
        try:
            prints = self._db.get_prints()
        except DBInternalError:
            return

        self.sio.emit("queues", prints_schema.jsonify(prints).json, broadcast=True)

    @classmethod
    def get_instance(cls) -> "SocketManager":
        # Note: Explicit use of class name to prevent issues with inheritance.
        if not SocketManager._instance:
            SocketManager._instance = cls()

        return SocketManager._instance

    _instance = None
