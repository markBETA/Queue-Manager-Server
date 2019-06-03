"""
This module implements the printer namespace resources test suite.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask_jwt_extended import create_access_token, decode_token
from flask_restplus import marshal

from queuemanager.api.files.models import file_model


def test_get_file(db_manager, jwt_blacklist_manager, http_client):
    user = db_manager.get_users(id=1)
    printer = db_manager.get_printers(id=1)
    file = db_manager.insert_file(user, "test", "./test-file.gcode")

    access_token = create_access_token({
        "type": "user",
        "id": printer.id,
        "serial_number": printer.serialNumber
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("api/files/1")
    assert r.status_code == 401
    assert r.json == {"message": "Missing Authorization Header"}

    r = http_client.get("api/files/1", headers={"Authorization": "Bearer "}, json={})
    assert r.status_code == 422
    assert r.json == {'message': "Bad Authorization header. Expected value 'Bearer <JWT>'"}

    r = http_client.get("/api/files/1", headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': 'Only printer access tokens are allowed.'}

    access_token = create_access_token({
        "type": "printer",
        # "id": printer.id,
        "serial_number": printer.serialNumber
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("/api/files/1", headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': "Can't retrieve the printer ID from the access token."}

    access_token = create_access_token({
        "type": "printer",
        "id": printer.id,
        "serial_number": printer.serialNumber
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("/api/files/100", headers=auth_header)
    assert r.status_code == 404
    assert r.json == {"message": "Can't find any file with this ID in the database."}

    r = http_client.get("/api/files/1", headers=auth_header)
    assert r.status_code == 401
    assert r.json == {'message': "This printer can't access to the requested file."}

    job = db_manager.insert_job("test-job", file, user)
    db_manager.enqueue_created_job(job)
    job.canBePrinted = True
    db_manager.commit_changes()
    db_manager.assign_job_to_printer(printer, job)

    r = http_client.get("/api/files/1", headers=auth_header)
    assert r.status_code == 200
    assert r.data.decode('utf-8') == open(file.fullPath, "r").read()
    assert r.headers[0] == ('Content-Disposition', 'attachment; filename=test')


def test_get_file_info(db_manager, jwt_blacklist_manager, http_client):
    user = db_manager.get_users(id=1)
    printer = db_manager.get_printers(id=1)
    file = db_manager.insert_file(user, "test", "./test-file.gcode")

    access_token = create_access_token({
        "type": "user",
        "id": printer.id,
        "serial_number": printer.serialNumber
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("api/files/1/info")
    assert r.status_code == 401
    assert r.json == {"message": "Missing Authorization Header"}

    r = http_client.get("api/files/1/info", headers={"Authorization": "Bearer "}, json={})
    assert r.status_code == 422
    assert r.json == {'message': "Bad Authorization header. Expected value 'Bearer <JWT>'"}

    r = http_client.get("/api/files/1/info", headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': 'Only printer access tokens are allowed.'}

    access_token = create_access_token({
        "type": "printer",
        # "id": printer.id,
        "serial_number": printer.serialNumber
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("/api/files/1/info", headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': "Can't retrieve the printer ID from the access token."}

    access_token = create_access_token({
        "type": "printer",
        "id": printer.id,
        "serial_number": printer.serialNumber
    })
    jwt_blacklist_manager.add_access_token(decode_token(access_token))
    auth_header = {"Authorization": "Bearer " + access_token}

    r = http_client.get("/api/files/100/info", headers=auth_header)
    assert r.status_code == 404
    assert r.json == {"message": "Can't find any file with this ID in the database."}

    r = http_client.get("/api/files/1/info", headers=auth_header)
    assert r.status_code == 401
    assert r.json == {'message': "This printer can't access to the requested file."}

    job = db_manager.insert_job("test-job", file, user)
    db_manager.enqueue_created_job(job)
    job.canBePrinted = True
    db_manager.commit_changes()
    db_manager.assign_job_to_printer(printer, job)

    r = http_client.get("/api/files/1/info", headers=auth_header)
    assert r.status_code == 200
    assert r.json == marshal(file, file_model, skip_none=True)
