"""
This module implements the printer namespace events testing.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from datetime import timedelta
from shutil import copyfile

from queuemanager.socketio import client_namespace


def test_emit_jobs_updated(socketio_client, db_manager):
    client_namespace.emit_jobs_updated(broadcast=True)

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'jobs_updated'
    assert received_events[0]['args'] == [None]


def test_emit_job_analyze_done(socketio_client, db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    client_namespace.emit_job_analyze_done(job, broadcast=True)

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'job_analyze_done'
    assert received_events[0]['args'][0] == {"id": job.id, "name": job.name}


def test_emit_job_analyze_error(socketio_client, db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    client_namespace.emit_job_analyze_error(job, "This is a test message", broadcast=True)

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'job_analyze_error'
    assert received_events[0]['args'][0] == {
        "job": {"id": job.id, "name": job.name},
        "message": "This is a test message",
        "additional_info": None
    }


def test_emit_job_enqueue_done(socketio_client, db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    client_namespace.emit_job_enqueue_done(job, broadcast=True)

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'job_enqueue_done'
    assert received_events[0]['args'][0] == {"id": job.id, "name": job.name}


def test_emit_job_enqueue_error(socketio_client, db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    client_namespace.emit_job_enqueue_error(job, "This is a test message", broadcast=True)

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'job_enqueue_error'
    assert received_events[0]['args'][0] == {
        "job": {"id": job.id, "name": job.name},
        "message": "This is a test message",
        "additional_info": None
    }


def test_emit_printer_data_updated(socketio_client, db_manager):
    printer = db_manager.get_printers(id=1)
    material = db_manager.get_printer_materials(id=1)
    extruder_type = db_manager.get_printer_extruder_types(id=4)
    db_manager.update_printer_extruder(printer.extruders[1], material=material, type=extruder_type)

    client_namespace.emit_printer_data_updated(printer, broadcast=True)

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'printer_data_updated'
    del received_events[0]['args'][0]["registered_at"]
    assert received_events[0]['args'][0] == {
        "total_printing_seconds": 0,
        "extruders": [
            {
                "index": 0,
                "type": None,
                "material": None
            },
            {
                "index": 1,
                "type": {
                    "id": 4,
                    "brand": "E3D",
                    "nozzle_diameter": 0.6
                },
                "material": {
                    "type": "PLA",
                    "bed_temp": 65,
                    "brand": None,
                    "print_temp": 215,
                    "guid": None,
                    "id": 1,
                    "color": None
                }
            }
        ],
        "total_failed_prints": 0,
        "model": {
            "name": "Sigmax",
            "id": 2,
            "depth": 297,
            "width": 420,
            "height": 210
        },
        "name": "default",
        "ip_address": None,
        "state": {
            "is_operational_state": False,
            "id": 1,
            "string": "Offline"
        },
        "total_success_prints": 0,
        "serial_number": "020.180622.3180",
        "id": 1,
        "current_job": None
    }


def test_emit_printer_temperatures_updated(socketio_client, db_manager):
    bed_temp = 55.1
    extruders_temp = [
        {
            "temp_value": 24.3,
            "index": 0,
        },
        {
            "temp_value": 215.7,
            "index": 1,
        }
    ]

    client_namespace.emit_printer_temperatures_updated(bed_temp, extruders_temp, broadcast=True)

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'printer_temperatures_updated'
    assert received_events[0]['args'][0] == {
        "bed_temp": 55.1,
        "extruders_temp": [
            {
                "temp_value": 24.3,
                "index": 0,
            },
            {
                "temp_value": 215.7,
                "index": 1,
            }
        ]
    }


def test_emit_job_progress_updated(socketio_client, db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test-file", "/home/Marc/test")
    job = db_manager.insert_job("test-job", file, user)
    job.progress = 1.2
    job.estimatedTimeLeft = timedelta(seconds=61.1)

    client_namespace.emit_job_progress_updated(job, broadcast=True)

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'job_progress_updated'
    assert received_events[0]['args'][0] == {
        "id": job.id,
        "name": job.name,
        "file_name": "test-file",
        "progress": 1.2,
        "estimated_seconds_left": 61.1
    }


def test_on_analyze_job(socketio_client, db_manager, file_manager):
    class FlaskFile(object):
        def __init__(self, filename, full_path):
            self.filename = filename
            self.origin_full_path = full_path

        def save(self, destination_path):
            copyfile(self.origin_full_path, destination_path)

    user = db_manager.get_users(id=1)
    helper_file = FlaskFile("test-file.gcode", "./test-file-no-header.gcode")
    file = file_manager.save_file(helper_file, user, analise_after_save=False)
    db_manager.insert_job("test-job-no-header", file, user)
    helper_file = FlaskFile("test-file.gcode", "./test-file.gcode")
    file = file_manager.save_file(helper_file, user, analise_after_save=False)
    db_manager.insert_job("test-job", file, user)

    socketio_client.emit("analyze_job", {"job_id": 100}, namespace="/client")

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'job_analyze_error'
    assert received_events[0]['args'][0] == {
        "job": {"id": 100, "name": None},
        "message": "There is no job with this ID in the database",
        "additional_info": None
    }


def test_on_enqueue_job(socketio_client, db_manager, file_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test-file", "/home/Marc/test")
    db_manager.insert_job("test-job", file, user)

    socketio_client.emit("enqueue_job", {"job_id": 100}, namespace="/client")

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'job_enqueue_error'
    assert received_events[0]['args'][0] == {
        "job": {"id": 100, "name": None},
        "message": "There is no job with this ID in the database",
        "additional_info": None
    }

    socketio_client.emit("enqueue_job", {"job_id": 1}, namespace="/client")

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 2
    assert received_events[0]['name'] == 'job_enqueue_done'
    assert received_events[0]['args'][0] == {"id": 1, "name": "test-job"}
    assert received_events[1]['name'] == 'jobs_updated'
    assert received_events[1]['args'] == [None]
