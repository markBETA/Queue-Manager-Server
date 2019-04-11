import os

import pytest

from queuemanager import create_app
from queuemanager.database import db as _db
from queuemanager.database import db_mgr
from queuemanager.file_storage import FileManager

TESTDB = 'test_project.db'
TESTDB_PATH = "{}".format(TESTDB)
TEST_DATABASE_URI = 'sqlite:///' + TESTDB_PATH
GCODE_STORAGE_PATH = './files/'


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + TESTDB_PATH,
        'SQLALCHEMY_TRACK_MODIFICATIONS': True,
        'FILE_MANAGER_UPLOAD_DIR': GCODE_STORAGE_PATH,
        'TEST_INPUTS_PATH': 'input',
        'SECRET_KEY': os.getenv('SECRET_KEY', 'my_secret_key')
    }
    app = create_app(__name__, settings_override)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    if os.path.exists(TESTDB_PATH):
        os.unlink(TESTDB_PATH)

    def teardown():
        _db.drop_all()
        if os.path.exists(TESTDB_PATH):
            os.unlink(TESTDB_PATH)

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope='function')
def db_manager(session):
    """Creates a new database DBManager instance for a test."""
    db_mgr.update_session(session)
    db_mgr.init_static_values()
    db_mgr.init_printers_state()
    db_mgr.init_jobs_can_be_printed()

    return db_mgr


@pytest.fixture(scope='function')
def file_manager(app, db_manager, request):
    file_manager = FileManager(app)

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
