import os

import pytest

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


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_BINDS': {'app': 'postgresql+psycopg2://postgres:dev@postgres.dev.server/app_test'},
        'SQLALCHEMY_TRACK_MODIFICATIONS': True,
        'FILE_MANAGER_UPLOAD_DIR': GCODE_STORAGE_PATH,
        'TEST_INPUTS_PATH': 'input',
        'SECRET_KEY': os.getenv('SECRET_KEY', 'my_secret_key')
    }
    enabled_modules = {
        "app-database",
        "file-storage",
        "socketio"
    }
    app = create_app(__name__, settings_override, enabled_modules=enabled_modules)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='function')
def db(app, request):
    """Session-wide test app_database."""
    if os.path.exists(TEST_DB_PATH):
        os.unlink(TEST_DB_PATH)

    def teardown():
        if os.path.exists(TEST_DB_PATH):
            os.unlink(TEST_DB_PATH)

    _db.drop_all()
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new app_database session for a test."""
    def teardown():
        db.session.close_all()

    request.addfinalizer(teardown)
    return db.session


@pytest.fixture(scope='function')
def db_manager(session):
    """Creates a new app_database DBManager instance for a test."""
    db_mgr.update_session(session)
    db_mgr.init_static_values()
    db_mgr.init_printers_state()
    db_mgr.init_jobs_can_be_printed()

    return db_mgr


# @pytest.fixture(scope='function')
# def jwt_blacklist_manager(app, request, db_manager):
#     from authserver.blacklist_manager import jwt_blacklist_manager
#
#     jwt_blacklist_manager.redis_store.flushdb()
#
#     def teardown():
#         jwt_blacklist_manager.redis_store.flushdb()
#
#     request.addfinalizer(teardown)
#     return jwt_blacklist_manager


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
def socketio_client(app, session, db_manager):
    socketio_client = socketio.test_client(app)
    socketio_client.connect("/client")
    socketio_client.connect("/printer")

    db_manager.update_session(session)

    socketio_mgr.set_db_manager(db_manager)

    return socketio_client