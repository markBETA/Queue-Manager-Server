"""
This module implements the printer namespace events testing.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.2"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from datetime import timedelta

from sqlalchemy.orm import Session

from queuemanager.file_storage import FileDescriptor
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
        "name": "Sigmax 4.0",
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


def test_on_analyze_job(socketio_client, client_session_key, db_manager, file_manager):
    user = db_manager.get_users(id=1)
    file_descriptor = FileDescriptor("test-file.gcode", path="./test-file-no-header.gcode")
    file = file_manager.save_file(file_descriptor, user)
    db_manager.insert_job("test-job-no-header", file, user)
    file_descriptor = FileDescriptor("test-file.gcode", path="./test-file.gcode")
    file = file_manager.save_file(file_descriptor, user)
    db_manager.insert_job("test-job", file, user)

    data = {"session_key": client_session_key, "job_id": 100}
    socketio_client.emit("analyze_job", data, namespace="/client")

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'job_analyze_error'
    assert received_events[0]['args'][0] == {
        "job": {"id": 100, "name": None},
        "message": "There is no job with this ID in the socketio_printer",
        "additional_info": None
    }

    job_no_header = db_manager.get_jobs(name="test-job-no-header")
    data = {"session_key": client_session_key, "job_id": job_no_header.id}
    socketio_client.emit("analyze_job", data, namespace="/client")

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'job_analyze_error'
    assert received_events[0]['args'][0] == {
        "job": {'id': 1, 'name': 'test-job-no-header'},
        "message": "The file data can't be loaded. Details: The file don't contain the data dictionary",
        "additional_info": None
    }

    job = db_manager.get_jobs(name="test-job")
    data = {"session_key": client_session_key, "job_id": job.id}
    Session.object_session(job)
    socketio_client.emit("analyze_job", data, namespace="/client")

    received_events = socketio_client.get_received("/client")
    job = db_manager.get_jobs(name="test-job")

    assert len(received_events) == 2
    assert received_events[0]['name'] == 'job_analyze_done'
    assert received_events[0]['args'][0] == {"id": job.id, "name": job.name}
    assert received_events[1]['name'] == 'jobs_updated'
    assert received_events[1]['args'] == [None]


def test_on_enqueue_job(app, socketio_client, socketio_printer, client_session_key, printer_session_key,
                        db_manager, file_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test-file", "/home/Marc/test")
    db_manager.insert_job("test-job", file, user)

    data = {"session_key": client_session_key, "job_id": 100}
    socketio_client.emit("enqueue_job", data, namespace="/client")

    received_events = socketio_client.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'job_enqueue_error'
    assert received_events[0]['args'][0] == {
        "job": {"id": 100, "name": None},
        "message": "There is no job with this ID in the socketio_printer",
        "additional_info": None
    }

    initial_data = {
        "session_key": printer_session_key,
        "state": "Ready",
        "extruders_info": [
            {
                "material_type": "PLA",
                "extruder_nozzle_diameter": 0.6,
                "index": 0
            },
            {
                "material_type": "ABS",
                "extruder_nozzle_diameter": 0.4,
                "index": 1
            },
        ]
    }

    socketio_printer.emit("initial_data", initial_data, namespace="/printer")

    socketio_client.get_received("/client")
    assert db_manager.get_printers(id=1).state.stateString == "Ready"

    job = db_manager.get_jobs(name="test-job")
    data = {"session_key": client_session_key, "job_id": job.id}
    socketio_client.emit("enqueue_job", data, namespace="/client")

    received_events = socketio_client.get_received("/client")
    job = db_manager.get_jobs(name="test-job")

    assert len(received_events) == 2
    assert received_events[0]['name'] == 'job_enqueue_done'
    assert received_events[0]['args'][0] == {"id": job.id, "name": job.name}
    assert received_events[1]['name'] == 'jobs_updated'
    assert received_events[1]['args'] == [None]

    received_events = socketio_printer.get_received("/printer")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'print_job'
    assert received_events[0]['args'][0] == {"id": job.id, "name": job.name, "file_id": job.file.id}
    assert db_manager.get_printers(id=1).idCurrentJob == job.id
