import os
import tempfile
import pytest
import shutil
from queuemanager import create_app
from queuemanager.db import db, init_db
from queuemanager.models.File import File
from queuemanager.models.Job import Job
from queuemanager.models.Queue import Queue
from queuemanager.models.User import User
from queuemanager.models.Extruder import Extruder
from tests.globals import GCODES


def populate_db(app):
    queue = Queue.query.filter_by(active=True).first()
    queue.used_extruders = [Extruder.query.filter_by(index=0, nozzle_diameter=0.6).first(),
                            Extruder.query.filter_by(index=1, nozzle_diameter=0.6).first()]
    user = User(username="eloi")
    user.hash_password("bcn3d")
    inputs_path = app.config.get("TEST_INPUTS_PATH")
    output_path = app.config.get("GCODE_STORAGE_PATH")
    for gcode in GCODES:
        job_name = gcode["job_name"]
        file_name = gcode["file_name"]
        time = gcode["time"]
        filament = gcode["filament"]
        extruders = gcode["extruders"]
        job = Job(name=job_name, user_id=user.id)
        filepath = os.path.join(output_path, file_name)
        file = File(name=file_name, path=filepath, time=time, used_material=filament)
        for index, value in extruders.items():
            extruder = Extruder.query.filter_by(index=index, nozzle_diameter=value).first()
            file.used_extruders.append(extruder)
        job.file = file
        queue.jobs.append(job)
        user.jobs.append(job)
        shutil.copyfile(os.path.join(inputs_path, file_name), os.path.join(output_path, file_name))

    db.session.commit()


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    gcodes_path = tempfile.mkdtemp()

    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path,
        'SQLALCHEMY_TRACK_MODIFICATIONS': True,
        'GCODE_STORAGE_PATH': gcodes_path,
        'TEST_INPUTS_PATH': 'input',
        'SECRET_KEY': os.getenv('SECRET_KEY', 'my_secret_key')
    })

    with app.app_context():
        init_db()
        populate_db(app)

    yield app

    os.close(db_fd)
    os.unlink(db_path)
    shutil.rmtree(gcodes_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
