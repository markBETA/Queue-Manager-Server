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

from flask_restplus import marshal

from queuemanager.api.files.models import file_model


def test_get_file(db_manager, http_client):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "./test-file.gcode")

    r = http_client.get("/api/files/100")
    assert r.status_code == 404
    assert r.json == {"message": "Can't find any file with this ID in the database"}

    r = http_client.get("/api/files/1")
    assert r.status_code == 200
    assert r.data.decode('utf-8') == open(file.fullPath, "r").read()
    assert r.headers[0] == ('Content-Disposition', 'attachment; filename=test')


def test_get_file_info(db_manager, http_client):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "./test-file.gcode")

    r = http_client.get("/api/files/100/info")
    assert r.status_code == 404
    assert r.json == {"message": "Can't find any file with this ID in the database"}

    r = http_client.get("/api/files/1/info")
    assert r.status_code == 200
    assert r.json == marshal(file, file_model, skip_none=True)
