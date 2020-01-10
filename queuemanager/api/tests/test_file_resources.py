"""
This module implements the file namespace API resources test suite.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

import json

from flask_restplus import marshal

from queuemanager.api.files.models import file_model


def test_get_file(db_manager, http_client, app):
    user = db_manager.get_users(id=1)
    printer = db_manager.get_printers(id=1)
    file = db_manager.insert_file(user, "test", "./test-file.gcode")

    auth_header = {"X-Identity": json.dumps({
        "type": "user",
        "id": user.id,
        "is_admin": True
    })}

    r = http_client.get("api/files/1")
    assert r.status_code == 401
    assert r.json == {"message": "Missing Identity Header"}

    r = http_client.get("api/files/1", headers={"X-Identity": "Bearer "}, json={})
    assert r.status_code == 422
    assert r.json == {'message': "Bad Authorization header. Expected JSON value"}

    r = http_client.get("/api/files/1", headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': 'Only printers are allowed to this API resource.'}

    auth_header = {"X-Identity": json.dumps({
        "type": "printer",
        "id": printer.id,
        "serial_number": printer.serialNumber
    })}

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
    assert ('Content-Disposition', 'attachment; filename=test') in list(r.headers)

    app.config["ENV"] = "production"

    r = http_client.get("/api/files/1", headers=auth_header)
    assert r.status_code == 200
    assert ('Content-Type', 'application/octet-stream') in list(r.headers)
    assert ('X-Accel-Redirect', '/files/1') in list(r.headers)
    assert ('Content-Disposition', 'attachment; filename="test"') in list(r.headers)
    assert ('Content-Length', '0') in list(r.headers)

    app.config["ENV"] = "development"


def test_get_file_info(db_manager, http_client):
    user = db_manager.get_users(id=1)
    printer = db_manager.get_printers(id=1)
    file = db_manager.insert_file(user, "test", "./test-file.gcode")

    auth_header = {"X-Identity": json.dumps({
        "type": "user",
        "id": user.id,
        "is_admin": True
    })}

    r = http_client.get("api/files/1/info")
    assert r.status_code == 401
    assert r.json == {"message": "Missing Identity Header"}

    r = http_client.get("api/files/1/info", headers={"X-Identity": "Bearer "}, json={})
    assert r.status_code == 422
    assert r.json == {'message': "Bad Authorization header. Expected JSON value"}

    r = http_client.get("/api/files/1/info", headers=auth_header)
    assert r.status_code == 422
    assert r.json == {'message': 'Only printers are allowed to this API resource.'}

    auth_header = {"X-Identity": json.dumps({
        "type": "printer",
        "id": printer.id,
        "serial_number": printer.serialNumber
    })}

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
