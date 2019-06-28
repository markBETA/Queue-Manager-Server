"""
This module implements the job namespace resources test suite.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.2"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

import os
from io import BytesIO
from shutil import copyfile

from flask_jwt_extended import create_access_token, decode_token
from flask_restplus import marshal

from queuemanager.api.jobs.models import job_model, job_state_model


def test_get_jobs(db_manager, jwt_blacklist_manager, http_client):
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

    access_token = create_access_token({
        "type": "printer",
        "id": printer.id,
        "serial_number": printer.serialNumber
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("api/jobs")
    assert r.status_code == 401
    assert r.json == {"message": "Missing Authorization Header"}

    r = http_client.get("api/jobs", headers={"Authorization": "Bearer "}, json={})
    assert r.status_code == 422
    assert r.json == {'message': "Bad Authorization header. Expected value 'Bearer <JWT>'"}

    r = http_client.get("api/jobs", headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': 'Only user access tokens are allowed.'}

    access_token = create_access_token({
        "type": "user",
        "id": user.id,
        "is_admin": True
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("api/jobs", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal(jobs, job_model, skip_none=True)

    r = http_client.get("api/jobs?id=1", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal(jobs[0], job_model, skip_none=True)

    r = http_client.get("api/jobs?id=a", headers=auth_header)
    assert r.status_code == 400
    assert r.json == {
       "errors": {"id": ['Not a valid integer.']},
       "message": "Query parameters validation failed."
    }

    r = http_client.get("api/jobs?id=100", headers=auth_header)
    assert r.status_code == 404
    assert r.json == {'message': 'The requested job don\'t exist.'}

    r = http_client.get("api/jobs?state=Waiting", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal(jobs[1:3], job_model, skip_none=True)

    r = http_client.get("api/jobs?state=fail", headers=auth_header)
    assert r.status_code == 400
    assert r.json == {
        "errors": {"state": ['Invalid value.']},
        "message": "Query parameters validation failed."
    }

    r = http_client.get("api/jobs?file_id=1", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal([jobs[0]], job_model, skip_none=True)

    r = http_client.get("api/jobs?user_id=1", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal(jobs, job_model, skip_none=True)

    r = http_client.get("api/jobs?user_id=2", headers=auth_header)
    assert r.status_code == 200
    assert r.json == []

    r = http_client.get("api/jobs?name=test-job-0", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal(jobs[0], job_model, skip_none=True)

    r = http_client.get("api/jobs?can_be_printed=true&state=Waiting", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal([jobs[2]], job_model, skip_none=True)

    db_manager.reorder_job_in_queue(jobs[1], jobs[2])

    r = http_client.get("api/jobs?&state=Waiting&order_by_priority=true", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal([jobs[2], jobs[1]], job_model, skip_none=True)


def test_create_job(db_manager, jwt_blacklist_manager, http_client, socketio_client, app):
    user = db_manager.get_users(id=1)

    access_token = create_access_token({
        "type": "printer",
        "id": 1,
        "serial_number": "000.00000.0000"
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.post('api/jobs/create')
    assert r.status_code == 401
    assert r.json == {"message": "Missing Authorization Header"}
    assert not socketio_client.get_received('/client')

    r = http_client.post('api/jobs/create', headers={"Authorization": "Bearer "}, json={})
    assert r.status_code == 422
    assert r.json == {'message': "Bad Authorization header. Expected value 'Bearer <JWT>'"}
    assert not socketio_client.get_received('/client')

    r = http_client.post('api/jobs/create', headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': 'Only user access tokens are allowed.'}
    assert not socketio_client.get_received('/client')

    access_token = create_access_token({
        "type": "user",
        # "id": user.id,
        "is_admin": True
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.post('api/jobs/create', headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': "Can't retrieve the user ID from the access token."}
    assert not socketio_client.get_received('/client')

    access_token = create_access_token({
        "type": "user",
        "id": user.id,
        "is_admin": True
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    wrong_data = {
        'name': 'test-job'
    }
    r = http_client.post('api/jobs/create', headers=auth_header, data=wrong_data)
    assert r.status_code == 400
    assert r.json == {'message': 'No file attached with the request.'}
    assert not socketio_client.get_received('/client')

    wrong_data = {
        'gcode': (BytesIO(open("./test-file.gcode").read().encode('utf-8')), 'test_file.gcode'),
    }
    r = http_client.post('api/jobs/create', headers=auth_header, data=wrong_data)
    assert r.status_code == 400
    assert r.json == {'message': 'No job name specified with the request.'}
    assert not socketio_client.get_received('/client')

    access_token_fail = create_access_token({
        "type": "user",
        "id": 100,
        "is_admin": True
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token_fail))
    auth_header_fail = {"Authorization": "Bearer " + access_token_fail}
    data = {
        'gcode': (BytesIO(open("./test-file.gcode").read().encode('utf-8')), 'test_file.gcode'),
        'name': 'test-job'
    }

    r = http_client.post('api/jobs/create', headers=auth_header_fail, data=data)
    assert r.status_code == 422
    assert r.json == {'message': "There isn't any registered user with the ID from the access token."}
    assert not socketio_client.get_received('/client')

    data = {
        'gcode': (BytesIO(open("./test-file.gcode").read().encode('utf-8')), 'test_file.gcode'),
        'name': 'test-job'
    }

    r = http_client.post('api/jobs/create', headers=auth_header, data=data)
    received_events = socketio_client.get_received('/client')
    assert r.status_code == 201
    assert r.json == marshal(db_manager.get_jobs(id=1), job_model, skip_none=True)
    assert len(received_events) == 1
    assert received_events[0]['name'] == 'jobs_updated'

    files = os.listdir('files/')
    assert len(files) == 1

    with open("./test-file.gcode") as expected_f:
        with open('files/'+files[0]) as f:
            assert expected_f.read() == f.read()
    os.unlink('files/'+files[0])

    data = {
        'gcode': (BytesIO(open("./test-file.gcode").read().encode('utf-8')), 'test_file.gcode'),
        'name': 'test-job'
    }
    r = http_client.post('api/jobs/create', headers=auth_header, data=data)
    assert r.status_code == 409
    assert r.json == {'message': 'Job name already exists.'}
    assert not socketio_client.get_received('/client')

    app.config["ENV"] = "production"

    data = {
        'gcode.name': 'test_file.gcode',
        'gcode.path': "./test-file.gcode",
        'name': 'test-job-2'
    }
    r = http_client.post('api/jobs/create', headers=auth_header, data=data)
    received_events = socketio_client.get_received('/client')
    assert r.status_code == 201
    assert r.json == marshal(db_manager.get_jobs(name="test-job-2"), job_model, skip_none=True)
    assert len(received_events) == 1
    assert received_events[0]['name'] == 'jobs_updated'

    files = os.listdir('files/')
    assert len(files) == 1

    with open("./test-file.gcode") as expected_f:
        with open('files/' + files[0]) as f:
            assert expected_f.read() == f.read()
    os.unlink('files/' + files[0])

    app.config["ENV"] = "development"


def test_get_not_done_jobs(db_manager, jwt_blacklist_manager, http_client):
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

    access_token = create_access_token({
        "type": "printer",
        "id": 1,
        "serial_number": "000.00000.0000"
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("api/jobs/not_done")
    assert r.status_code == 401
    assert r.json == {"message": "Missing Authorization Header"}

    r = http_client.get("api/jobs/not_done", headers={"Authorization": "Bearer "}, json={})
    assert r.status_code == 422
    assert r.json == {'message': "Bad Authorization header. Expected value 'Bearer <JWT>'"}

    r = http_client.get("api/jobs/not_done", headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': 'Only user access tokens are allowed.'}

    access_token = create_access_token({
        "type": "user",
        "id": user.id,
        "is_admin": True
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("api/jobs/not_done?order_by_priority=fail", headers=auth_header)
    assert r.status_code == 400
    assert r.json == {
        "errors": {"order_by_priority": ['Not a valid boolean.']},
        "message": "Query parameters validation failed."
    }

    r = http_client.get("api/jobs/not_done", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal(jobs[:4], job_model, skip_none=True)

    db_manager.reorder_job_in_queue(jobs[1], jobs[2])

    r = http_client.get("api/jobs/not_done?order_by_priority=true", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal([jobs[0], jobs[2], jobs[1], jobs[3]], job_model, skip_none=True)


def test_get_job_states(db_manager, jwt_blacklist_manager, http_client):
    job_states = db_manager.get_job_states()
    user = db_manager.get_users(id=1)

    access_token = create_access_token({
        "type": "printer",
        "id": 1,
        "serial_number": "000.00000.0000"
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("api/jobs/states")
    assert r.status_code == 401
    assert r.json == {"message": "Missing Authorization Header"}

    r = http_client.get("api/jobs/states", headers={"Authorization": "Bearer "}, json={})
    assert r.status_code == 422
    assert r.json == {'message': "Bad Authorization header. Expected value 'Bearer <JWT>'"}

    r = http_client.get("api/jobs/states", headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': 'Only user access tokens are allowed.'}

    access_token = create_access_token({
        "type": "user",
        "id": user.id,
        "is_admin": True
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("api/jobs/states", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal(job_states, job_state_model)


def test_get_job(db_manager, jwt_blacklist_manager, http_client):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    access_token = create_access_token({
        "type": "printer",
        "id": 1,
        "serial_number": "000.00000.0000"
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("api/jobs/"+str(job.id))
    assert r.status_code == 401
    assert r.json == {"message": "Missing Authorization Header"}

    r = http_client.get("api/jobs/"+str(job.id), headers={"Authorization": "Bearer "}, json={})
    assert r.status_code == 422
    assert r.json == {'message': "Bad Authorization header. Expected value 'Bearer <JWT>'"}

    r = http_client.get("api/jobs/"+str(job.id), headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': 'Only user access tokens are allowed.'}

    access_token = create_access_token({
        "type": "user",
        "id": user.id,
        "is_admin": True
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("api/jobs/100", headers=auth_header)
    assert r.status_code == 404
    assert r.json == {'message': 'There is no job with this ID in the database.'}

    r = http_client.get("api/jobs/"+str(job.id), headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal(job, job_model, skip_none=True)


def test_delete_job(db_manager, jwt_blacklist_manager, http_client):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "./test-file.gcode")
    job = db_manager.insert_job("test", file, user)

    access_token = create_access_token({
        "type": "printer",
        "id": 1,
        "serial_number": "000.00000.0000"
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.delete("api/jobs/" + str(job.id))
    assert r.status_code == 401
    assert r.json == {"message": "Missing Authorization Header"}

    r = http_client.delete("api/jobs/" + str(job.id), headers={"Authorization": "Bearer "}, json={})
    assert r.status_code == 422
    assert r.json == {'message': "Bad Authorization header. Expected value 'Bearer <JWT>'"}

    r = http_client.delete("api/jobs/" + str(job.id), headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': 'Only user access tokens are allowed.'}

    access_token = create_access_token({
        "type": "user",
        # "id": user.id,
        "is_admin": True
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.delete("api/jobs/" + str(job.id), headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': "Can't retrieve the user ID from the access token."}

    access_token = create_access_token({
        "type": "user",
        "id": 2,
        "is_admin": False
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.delete("api/jobs/"+str(job.id)+"?delete_file=fail", headers=auth_header)
    assert r.status_code == 400
    assert r.json == {
        "errors": {"delete_file": ['Not a valid boolean.']},
        "message": "Query parameters validation failed."
    }

    r = http_client.delete("api/jobs/100", headers=auth_header)
    assert r.status_code == 404
    assert r.json == {'message': 'There is no job with this ID in the database.'}

    r = http_client.delete("api/jobs/" + str(job.id) + "?delete_file=false", headers=auth_header)
    assert r.status_code == 401
    assert r.json == {'message': "Only admin users can delete a job created by another user."}

    access_token = create_access_token({
        "type": "user",
        "id": user.id,
        "is_admin": False
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.delete("api/jobs/"+str(job.id)+"?delete_file=false", headers=auth_header)
    assert r.status_code == 200
    assert r.json == {'message': 'Job <{}> deleted from the database.'.format(job.name)}

    assert os.path.exists("./test-file.gcode")
    assert db_manager.get_jobs(id=job.id) is None

    job = db_manager.insert_job("test", file, user)

    access_token = create_access_token({
        "type": "user",
        "id": 2,
        "is_admin": True
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.delete("api/jobs/" + str(job.id) + "?delete_file=false", headers=auth_header)
    assert r.status_code == 200
    assert r.json == {'message': 'Job <{}> deleted from the database.'.format(job.name)}

    if not os.path.exists("./test-file-delete.gcode"):
        copyfile("./test-file.gcode", "./test-file-delete.gcode")
    file = db_manager.insert_file(user, "test", "./test-file-delete.gcode")
    job = db_manager.insert_job("test", file, user)

    r = http_client.delete("api/jobs/"+str(job.id), headers=auth_header)
    assert r.status_code == 200
    assert r.json == {'message': 'Job <{}> deleted from the database.'.format(job.name)}

    assert not os.path.exists("./test-file-delete.gcode")
    assert db_manager.get_jobs(id=job.id) is None


def test_put_job(db_manager, jwt_blacklist_manager, http_client):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "./test-file.gcode")
    job = db_manager.insert_job("test", file, user)

    access_token = create_access_token({
        "type": "printer",
        "id": 1,
        "serial_number": "000.00000.0000"
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.put("api/jobs/" + str(job.id), json={})
    assert r.status_code == 401
    assert r.json == {"message": "Missing Authorization Header"}

    r = http_client.put("api/jobs/" + str(job.id), headers={"Authorization": "Bearer "}, json={})
    assert r.status_code == 422
    assert r.json == {'message': "Bad Authorization header. Expected value 'Bearer <JWT>'"}

    r = http_client.put("api/jobs/" + str(job.id), headers=auth_header, json={})
    assert r.status_code == 422
    assert r.json == {'message': 'Only user access tokens are allowed.'}

    access_token = create_access_token({
        "type": "user",
        # "id": user.id,
        "is_admin": True
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.put("api/jobs/" + str(job.id), headers=auth_header, json={})
    assert r.status_code == 422
    assert r.json == {'message': "Can't retrieve the user ID from the access token."}

    access_token = create_access_token({
        "type": "user",
        "id": 2,
        "is_admin": False
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.put("api/jobs/100", headers=auth_header, json={})
    assert r.status_code == 404
    assert r.json == {'message': 'There is no job with this ID in the database.'}

    r = http_client.put("api/jobs/" + str(job.id), headers=auth_header, json={"name": "test1"})
    assert r.status_code == 401
    assert r.json == {'message': 'Only admin users can delete a job created by another user.'}

    access_token = create_access_token({
        "type": "user",
        "id": user.id,
        "is_admin": False
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.put("api/jobs/" + str(job.id), headers=auth_header, json={"name": "test1"})
    job = db_manager.get_jobs(id=job.id)
    assert r.status_code == 200
    assert r.json == marshal(job, job_model, skip_none=True)

    access_token = create_access_token({
        "type": "user",
        "id": 2,
        "is_admin": True
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.put("api/jobs/1", headers=auth_header, json={"don't_fail": 0, "name": "test2"})
    job = db_manager.get_jobs(id=job.id)
    assert r.status_code == 200
    assert r.json == marshal(job, job_model, skip_none=True)

    db_manager.insert_job("test", file, user)

    r = http_client.put("api/jobs/" + str(job.id), headers=auth_header, json={"name": "test"})
    assert r.status_code == 409
    assert r.json == {'message': 'Job name already exists.'}


def test_reorder_job(db_manager, jwt_blacklist_manager, http_client):
    user = db_manager.get_users(id=1)
    files = []
    jobs = []
    for i in range(4):
        files.append(db_manager.insert_file(user, "test-file-{}".format(str(i)), "/home/Marc/test{}".format(str(i))))
        jobs.append(db_manager.insert_job("test-job-{}".format(str(i)), files[-1], user))
        db_manager.enqueue_created_job(jobs[i])

    access_token = create_access_token({
        "type": "printer",
        "id": 1,
        "serial_number": "000.00000.0000"
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.put("api/jobs/1/reorder", json={"previous_job_id": 2})
    assert r.status_code == 401
    assert r.json == {"message": "Missing Authorization Header"}

    r = http_client.put("api/jobs/1/reorder", headers={"Authorization": "Bearer "}, json={"previous_job_id": 2})
    assert r.status_code == 422
    assert r.json == {'message': "Bad Authorization header. Expected value 'Bearer <JWT>'"}

    r = http_client.put("api/jobs/1/reorder", headers=auth_header, json={"previous_job_id": 2})
    assert r.status_code == 422
    assert r.json == {'message': 'Only user access tokens are allowed.'}

    access_token = create_access_token({
        "type": "user",
        "id": user.id,
        "is_admin": False
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.put("api/jobs/1/reorder", headers=auth_header, json={"previous_job_id": 2})
    assert r.status_code == 401
    assert r.json == {'message': "Only admin users can reorder jobs."}

    access_token = create_access_token({
        "type": "user",
        "id": user.id,
        "is_admin": True
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.put("api/jobs/100/reorder", headers=auth_header, json={"previous_job_id": 2})
    assert r.status_code == 404
    assert r.json == {'message': 'There is no job with this ID in the database.'}

    r = http_client.put("api/jobs/1/reorder", headers=auth_header, json={"fail": 0})
    assert r.status_code == 400
    assert r.json == {
        'errors': {'previous_job_id': "'previous_job_id' is a required property"},
        'message': 'Input payload validation failed'
    }

    r = http_client.put("api/jobs/1/reorder", headers=auth_header, json={"previous_job_id": 100})
    assert r.status_code == 404
    assert r.json == {"message": 'There is no job with this ID in the database.'}

    r = http_client.put("api/jobs/1/reorder", headers=auth_header, json={"previous_job_id": "fail"})
    assert r.status_code == 400
    assert r.json == {
        'errors': {'previous_job_id': "'fail' is not of type 'integer'"},
        'message': 'Input payload validation failed'
    }

    r = http_client.put("api/jobs/1/reorder", headers=auth_header, json={"previous_job_id": 2})
    assert r.status_code == 200
    assert r.json == {'message': 'Job <test-job-0> reordered successfully.'}

    jobs = db_manager.get_jobs()

    r = http_client.get("api/jobs?&state=Waiting&order_by_priority=true", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal([jobs[1], jobs[0], jobs[2], jobs[3]], job_model, skip_none=True)


def test_reprint_job(db_manager, jwt_blacklist_manager, http_client, socketio_client, socketio_printer):
    user = db_manager.get_users(id=1)
    printer = db_manager.get_printers(id=1)
    files = []
    jobs = []
    for i in range(4):
        files.append(db_manager.insert_file(user, "test-file-{}".format(str(i)), "/home/Marc/test{}".format(str(i))))
        jobs.append(db_manager.insert_job("test-job-{}".format(str(i)), files[-1], user))
        db_manager.enqueue_created_job(jobs[i])
    db_manager.update_job(jobs[0], canBePrinted=True)
    db_manager.assign_job_to_printer(printer, jobs[0])
    db_manager.set_printing_job(jobs[0])
    db_manager.set_finished_job(jobs[0])
    db_manager.set_done_job(jobs[0], True)
    job_id = jobs[0].id

    access_token = create_access_token({
        "type": "printer",
        "id": 1,
        "serial_number": "000.00000.0000"
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.put("api/jobs/" + str(job_id) + "/reprint", json={"previous_job_id": 2})
    assert r.status_code == 401
    assert r.json == {"message": "Missing Authorization Header"}

    r = http_client.put("api/jobs/" + str(job_id) + "/reprint", headers={"Authorization": "Bearer "})
    assert r.status_code == 422
    assert r.json == {'message': "Bad Authorization header. Expected value 'Bearer <JWT>'"}

    r = http_client.put("api/jobs/" + str(job_id) + "/reprint", headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': 'Only user access tokens are allowed.'}

    access_token = create_access_token({
        "type": "user",
        "id": user.id,
        "is_admin": False
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.put("api/jobs/100/reprint", headers=auth_header)
    assert r.status_code == 404
    assert r.json == {'message': 'There is no job with this ID in the database.'}

    jobs = db_manager.get_jobs()

    r = http_client.get("api/jobs?&state=Waiting&order_by_priority=true", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal([jobs[1], jobs[2], jobs[3]], job_model, skip_none=True)

    r = http_client.put("api/jobs/" + str(job_id) + "/reprint", headers=auth_header)
    assert r.status_code == 200
    assert r.json == {'message': 'Job <test-job-0> enqueued for reprint.'}
    assert socketio_client.get_received("/client") == [{'args': [None], 'name': 'jobs_updated', 'namespace': '/client'}]
    assert socketio_printer.get_received("/printer") == []

    jobs = db_manager.get_jobs()

    r = http_client.get("api/jobs?&state=Waiting&order_by_priority=true", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal([jobs[1], jobs[2], jobs[3], jobs[0]], job_model, skip_none=True)
