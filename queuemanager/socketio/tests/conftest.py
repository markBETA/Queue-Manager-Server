import os
import json
import pytest

from sqlalchemy.orm import close_all_sessions

from ... import create_app
from ...database import db as _db
from ...database import db_mgr
from ...file_storage import FileManager
from ...socketio import socketio, socketio_mgr

TEST_DB = 'test.db'
TEST_DB_PATH = "{}".format(TEST_DB)
TEST_DB_URI = 'sqlite:///' + TEST_DB_PATH
GCODE_STORAGE_PATH = './files/'

os.chdir(os.path.dirname(__file__))

_client_session_key = None
_printer_session_key = None


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    enabled_modules = {
        "app-database",
        "file-storage",
        "socketio",
        "identity-mgr"
    }
    app = create_app(__name__, testing=True, enabled_modules=enabled_modules)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='function')
def db(app, request):
    """Session-wide test socketio_printer."""
    if os.path.exists(TEST_DB_PATH):
        os.unlink(TEST_DB_PATH)

    def teardown():
        if os.path.exists(TEST_DB_PATH):
            os.unlink(TEST_DB_PATH)

    _db.drop_all()
    _db.create_all()
    _db.session.expunge_all()
    _db.session.remove()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new socketio_printer session for a test."""
    db.session = db.create_scoped_session()

    def teardown():
        db.session.expunge_all()
        close_all_sessions()

    request.addfinalizer(teardown)
    return db.session


@pytest.fixture(scope='function')
def db_manager(app, session):
    """Creates a new socketio_printer DBManager instance for a test."""
    db_mgr.init_app(app)
    db_mgr.update_session(session)
    db_mgr.init_static_values()
    db_mgr.init_printers_state()
    db_mgr.init_jobs_can_be_printed()

    return db_mgr


@pytest.fixture(scope='function')
def file_manager(app, db_manager, request):
    file_manager = FileManager(app, db_manager=db_manager)

    def teardown():
        for the_file in os.listdir(app.config['FILE_MANAGER_UPLOAD_DIR']):
            file_path = os.path.join(app.config['FILE_MANAGER_UPLOAD_DIR'], the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    os.rmdir(file_path)
            except Exception as e:
                print(e)

    request.addfinalizer(teardown)
    return file_manager


@pytest.fixture(scope='function')
def socketio_client(app, session, db_manager, request):
    global _client_session_key

    socketio_client = socketio.test_client(app)

    auth_header = {"X-Identity": json.dumps({
        "type": "user",
        "id": 1,
        "is_admin": True
    })}

    socketio_client.connect("/client", headers=auth_header)

    _client_session_key = None

    for received_event in socketio_client.get_received('/client'):
        if received_event['name'] == 'session_key':
            _client_session_key = received_event['args'][0]

    if _client_session_key is None:
        raise RuntimeError("No session key received after successful connection.")

    db_manager.update_session(session)

    socketio_mgr.set_db_manager(db_manager)

    def teardown():
        socketio_client.disconnect()

    request.addfinalizer(teardown)

    return socketio_client


@pytest.fixture(scope='function')
def socketio_printer(app, session, db_manager, request):
    global _printer_session_key

    socketio_client = socketio.test_client(app)

    auth_header = {"X-Identity": json.dumps({
        "type": "printer",
        "id": 1,
        "serial_number": "020.238778.0823"
    })}

    socketio_client.connect("/printer", headers=auth_header)

    _printer_session_key = None

    for received_event in socketio_client.get_received('/printer'):
        if received_event['name'] == 'session_key':
            _printer_session_key = received_event['args'][0]

    if _printer_session_key is None:
        raise RuntimeError("No session key received after successful connection.")

    db_manager.update_session(session)

    socketio_mgr.set_db_manager(db_manager)

    def teardown():
        socketio_client.disconnect()

    request.addfinalizer(teardown)

    return socketio_client


@pytest.fixture(scope='function')
def client_session_key():
    global _client_session_key
    return _client_session_key


@pytest.fixture(scope='function')
def printer_session_key():
    global _printer_session_key
    return _printer_session_key
