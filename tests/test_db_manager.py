import pytest
from queuemanager.db_manager import DBManager
from queuemanager.models.Queue import Queue


@pytest.fixture
def db():
    return DBManager()


def test_update_queue(app, db):
    with app.app_context():
        printer_info = {
            "hed_0": "0.4",
            "hed_1": "0.6"
        }
        db.update_queue(printer_info)
        active_queue = Queue.query.filter_by(active=True).first()
        for i in range(0, len(active_queue.jobs)):
            job = active_queue.jobs[i]
            assert set(job.file.used_extruders) <= set(active_queue.used_extruders)
            assert job.order == i + 1

        waiting_queue = Queue.query.filter_by(active=False).first()
        for i in range(0, len(waiting_queue.jobs)):
            job = waiting_queue.jobs[i]
            assert set(job.file.used_extruders) != set(active_queue.used_extruders) and job.file.used_extruders
            assert job.order == i + 1
