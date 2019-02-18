import os
import tempfile

import pytest
from queuemanager import create_app
from queuemanager.db import db, init_db
from queuemanager.models.File import File
from queuemanager.models.Job import Job
from queuemanager.models.Queue import Queue
from queuemanager.models.Extruder import Extruder


def populate_db():
    pass


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path,
        'SQLALCHEMY_TRACK_MODIFICATIONS': True,
        'GCODE_STORAGE_PATH': 'gcodes'
    })

    with app.app_context():
        init_db()
        populate_db()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
