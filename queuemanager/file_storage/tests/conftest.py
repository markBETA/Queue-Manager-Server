import os
import pytest

from sqlalchemy.orm import close_all_sessions

from ... import create_app
from ...database import db as _db
from ...database import db_mgr
from ...file_storage import FileManager

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
        "file-storage"
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
            except Exception as e:
                print(e)

    request.addfinalizer(teardown)
    return file_manager
