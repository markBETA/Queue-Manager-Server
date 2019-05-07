"""
This module implements the job namespace resources test suite.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

import os
from io import BytesIO
from shutil import copyfile

from flask_restplus import marshal

from queuemanager.api.jobs.models import job_model


def test_get_jobs(db_manager, http_client):
    user = db_manager.get_users(id=1)
    printer = db_manager.get_printers(id=1)
    files = []
    jobs = []
    for i in range(5):
        files.append(db_manager.insert_file(user, "test-file-{}".format(str(i)), "/home/Marc/test{}".format(str(i))))
        jobs.append(db_manager.insert_job("test-job-{}".format(str(i)), files[-1], user))
        if i > 0:
            db_manager.enqueue_created_job(jobs[-1])
        if i == 2:
            db_manager.update_job(jobs[i], canBePrinted=True)
        elif i == 3:
            db_manager.update_job(jobs[i], canBePrinted=True)
            db_manager.update_printer(printer, idCurrentJob=jobs[i].id)
            db_manager.set_printing_job(jobs[i])
        elif i == 4:
            db_manager.update_job(jobs[i], canBePrinted=True)
            db_manager.update_printer(printer, idCurrentJob=jobs[i].id)
            db_manager.set_printing_job(jobs[i])
            db_manager.set_finished_job(jobs[i])

    r = http_client.get("api/jobs")
    assert r.status_code == 200
    assert r.json == marshal(jobs, job_model, skip_none=True)

    r = http_client.get("api/jobs?id=1")
    assert r.status_code == 200
    assert r.json == marshal(jobs[0], job_model, skip_none=True)

    r = http_client.get("api/jobs?id=a")
    assert r.status_code == 400
    assert r.json == {
       "errors": {"id": ['Not a valid integer.']},
       "message": "Query parameters validation failed"
    }

    r = http_client.get("api/jobs?id=100")
    assert r.status_code == 404
    assert r.json == {'message': 'The requested job don\'t exist'}

    r = http_client.get("api/jobs?state=Waiting")
    assert r.status_code == 200
    assert r.json == marshal(jobs[1:3], job_model, skip_none=True)

    r = http_client.get("api/jobs?state=fail")
    assert r.status_code == 400
    assert r.json == {
        "errors": {"state": ['Invalid value.']},
        "message": "Query parameters validation failed"
    }

    r = http_client.get("api/jobs?file_id=1")
    assert r.status_code == 200
    assert r.json == marshal([jobs[0]], job_model, skip_none=True)

    r = http_client.get("api/jobs?user_id=1")
    assert r.status_code == 200
    assert r.json == marshal(jobs, job_model, skip_none=True)

    r = http_client.get("api/jobs?user_id=2")
    assert r.status_code == 200
    assert r.json == []

    r = http_client.get("api/jobs?name=test-job-0")
    assert r.status_code == 200
    assert r.json == marshal(jobs[0], job_model, skip_none=True)

    r = http_client.get("api/jobs?can_be_printed=true&state=Waiting")
    assert r.status_code == 200
    assert r.json == marshal([jobs[2]], job_model, skip_none=True)

    db_manager.reorder_job_in_queue(jobs[1], jobs[2])

    r = http_client.get("api/jobs?&state=Waiting&order_by_priority=true")
    assert r.status_code == 200
    assert r.json == marshal([jobs[2], jobs[1]], job_model, skip_none=True)


def test_post_job(db_manager, http_client, socketio_client):
    wrong_data = {
        'name': 'test-job'
    }
    r = http_client.post('/api/jobs', data=wrong_data)
    assert r.status_code == 400
    assert r.json == {'message': 'No file attached with the request'}

    wrong_data = {
        'gcode': (BytesIO(open("./test-file.gcode").read().encode('utf-8')), 'test_file.gcode'),
    }
    r = http_client.post('/api/jobs', data=wrong_data)
    assert r.status_code == 400
    assert r.json == {'message': 'No job name specified with the request'}

    data = {
        'gcode': (BytesIO(open("./test-file.gcode").read().encode('utf-8')), 'test_file.gcode'),
        'name': 'test-job'
    }
    r = http_client.post('/api/jobs', data=data)
    assert r.status_code == 201
    assert r.json == marshal(db_manager.get_jobs(id=1), job_model, skip_none=True)

    files = os.listdir('files/')
    assert len(files) == 1
    assert open("./test-file.gcode").read() == open('files/'+files[0]).read()


def test_get_not_done_jobs(db_manager, http_client):
    user = db_manager.get_users(id=1)
    printer = db_manager.get_printers(id=1)
    files = []
    jobs = []
    for i in range(5):
        files.append(db_manager.insert_file(user, "test-file-{}".format(str(i)), "/home/Marc/test{}".format(str(i))))
        jobs.append(db_manager.insert_job("test-job-{}".format(str(i)), files[-1], user))
        db_manager.enqueue_created_job(jobs[i])
        if i == 4:
            db_manager.update_job(jobs[i], canBePrinted=True)
            db_manager.update_printer(printer, idCurrentJob=jobs[i].id)
            db_manager.set_printing_job(jobs[i])
            db_manager.set_finished_job(jobs[i])
            db_manager.set_done_job(jobs[i], succeed=True)

    r = http_client.get("api/jobs/not_done?order_by_priority=fail")
    assert r.status_code == 400
    assert r.json == {
        "errors": {"order_by_priority": ['Not a valid boolean.']},
        "message": "Query parameters validation failed"
    }

    r = http_client.get("api/jobs/not_done")
    assert r.status_code == 200
    assert r.json == marshal(jobs[:4], job_model, skip_none=True)

    db_manager.reorder_job_in_queue(jobs[1], jobs[2])

    r = http_client.get("api/jobs/not_done?order_by_priority=true")
    assert r.status_code == 200
    assert r.json == marshal([jobs[0], jobs[2], jobs[1], jobs[3]], job_model, skip_none=True)


def test_get_job(db_manager, http_client):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    r = http_client.get("api/jobs/100")
    assert r.status_code == 404
    assert r.json == {'message': 'There is no job with this ID in the database'}

    r = http_client.get("api/jobs/"+str(job.id))
    assert r.status_code == 200
    assert r.json == marshal(job, job_model, skip_none=True)


def test_delete_job(db_manager, http_client):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "./test-file.gcode")
    job = db_manager.insert_job("test", file, user)

    r = http_client.delete("api/jobs/1?delete_file=fail")
    assert r.status_code == 400
    assert r.json == {
        "errors": {"delete_file": ['Not a valid boolean.']},
        "message": "Query parameters validation failed"
    }

    r = http_client.delete("api/jobs/100")
    assert r.status_code == 404
    assert r.json == {'message': 'There is no job with this ID in the database'}

    r = http_client.delete("api/jobs/1?delete_file=false")
    assert r.status_code == 200
    assert r.json == {'message': 'Job <{}> deleted from the database'.format(job.name)}

    assert os.path.exists("./test-file.gcode")
    assert db_manager.get_jobs(id=1) is None

    if not os.path.exists("./test-file-delete.gcode"):
        copyfile("./test-file.gcode", "./test-file-delete.gcode")
    file = db_manager.insert_file(user, "test", "./test-file-delete.gcode")
    job = db_manager.insert_job("test", file, user)

    r = http_client.delete("api/jobs/1")
    assert r.status_code == 200
    assert r.json == {'message': 'Job <{}> deleted from the database'.format(job.name)}

    assert not os.path.exists("./test-file-delete.gcode")
    assert db_manager.get_jobs(id=2) is None


def test_put_job(db_manager, http_client):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "./test-file.gcode")
    db_manager.insert_job("test", file, user)

    r = http_client.put("api/jobs/100", json={})
    assert r.status_code == 404
    assert r.json == {'message': 'There is no job with this ID in the database'}

    r = http_client.put("api/jobs/1", json={"fail": 0, "name": "test1"})
    assert r.status_code == 500
    assert r.json == {"message": "Invalid \'fail\' parameter"}

    job = db_manager.get_jobs(id=1)

    r = http_client.put("api/jobs/1", json={"name": "test1"})
    assert r.status_code == 200
    assert r.json == marshal(job, job_model, skip_none=True)


def test_reorder_job(db_manager, http_client):
    user = db_manager.get_users(id=1)
    files = []
    jobs = []
    for i in range(4):
        files.append(db_manager.insert_file(user, "test-file-{}".format(str(i)), "/home/Marc/test{}".format(str(i))))
        jobs.append(db_manager.insert_job("test-job-{}".format(str(i)), files[-1], user))
        db_manager.enqueue_created_job(jobs[i])

    r = http_client.put("api/jobs/100/reorder", json={"previous_job_id": 2})
    assert r.status_code == 404
    assert r.json == {'message': 'There is no job with this ID in the database'}

    r = http_client.put("api/jobs/1/reorder", json={"fail": 0})
    assert r.status_code == 400
    assert r.json == {
        'errors': {'previous_job_id': "'previous_job_id' is a required property"},
        'message': 'Input payload validation failed'
    }

    r = http_client.put("api/jobs/1/reorder", json={"previous_job_id": 100})
    assert r.status_code == 404
    assert r.json == {"message": 'There is no job with this ID in the database'}

    r = http_client.put("api/jobs/1/reorder", json={"previous_job_id": "fail"})
    assert r.status_code == 400
    assert r.json == {
        'errors': {'previous_job_id': "'fail' is not of type 'integer'"},
        'message': 'Input payload validation failed'
    }

    r = http_client.put("api/jobs/1/reorder", json={"previous_job_id": 2})
    assert r.status_code == 200
    assert r.json == {'message': 'Job <test-job-0> reordered successfully'}

    jobs = db_manager.get_jobs()

    r = http_client.get("api/jobs?&state=Waiting&order_by_priority=true")
    assert r.status_code == 200
    assert r.json == marshal([jobs[1], jobs[0], jobs[2], jobs[3]], job_model, skip_none=True)
