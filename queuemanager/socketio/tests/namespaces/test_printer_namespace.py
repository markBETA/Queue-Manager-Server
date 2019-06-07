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

from queuemanager.socketio import printer_namespace


def test_printer_connected(socketio_printer):
    received_events = socketio_printer.get_received("/client")

    assert len(received_events) == 0


def test_printer_disconnected(socketio_printer, db_manager):
    printer = db_manager.get_printers(id=1)

    db_manager.update_printer(printer, idState=db_manager.printer_state_ids["Ready"], sid=socketio_printer.sid)

    assert printer.idState == db_manager.printer_state_ids["Ready"]

    socketio_printer.disconnect("/printer")

    received_events = socketio_printer.get_received("/client")

    assert len(received_events) == 2
    assert received_events[0]['name'] == 'printer_data_updated'
    assert received_events[0]['args'][0]['state']['string'] == "Offline"
    assert received_events[1]['name'] == 'jobs_updated'
    assert received_events[1]['args'] == [None]


def test_emit_print_job(socketio_printer, db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    printer_namespace.emit_print_job(job, broadcast=True)

    received_events = socketio_printer.get_received(namespace="/printer")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'print_job'
    assert received_events[0]['namespace'] == '/printer'
    assert len(received_events[0]['args']) == 1
    for k, v in received_events[0]['args'][0].items():
        if k == "file_id":
            assert v == 1
        elif k == "name":
            assert v == 'test'
        elif k == "id":
            assert v == 1
        else:
            assert False


def test_emit_job_recovered(socketio_printer, db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)
    printer = db_manager.get_printers(id=1)
    db_manager.enqueue_created_job(job)
    db_manager.update_job(job, canBePrinted=True)
    db_manager.assign_job_to_printer(printer, job)
    db_manager.set_printing_job(job)

    printer_namespace.emit_job_recovered(job, broadcast=True)

    received_events = socketio_printer.get_received(namespace="/printer")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'job_recovered'
    assert received_events[0]['namespace'] == '/printer'
    assert len(received_events[0]['args']) == 1
    for k, v in received_events[0]['args'][0].items():
        if k == "id":
            assert v == 1
        elif k == "name":
            assert v == "test"
        elif k == "started_at":
            assert isinstance(v, str)
        elif k == "interrupted":
            assert v is False
        else:
            assert False


def test_on_initial_data(socketio_printer, printer_session_key, db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)
    printer = db_manager.get_printers(id=1)
    db_manager.enqueue_created_job(job)
    db_manager.update_job(job, canBePrinted=True)
    db_manager.assign_job_to_printer(printer, job)
    db_manager.set_printing_job(job)

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

    printer = db_manager.get_printers(id=1)

    assert printer.state.stateString == "Offline"

    socketio_printer.emit("initial_data", initial_data, namespace="/printer")

    received_events = socketio_printer.get_received("/client")

    assert len(received_events) == 4
    assert received_events[0]['name'] == 'printer_data_updated'
    assert received_events[0]['args'][0]['state']['string'] == "Ready"
    for extruder in received_events[0]['args'][0]['extruders']:
        if extruder['index'] == 0:
            assert extruder['material']['type'] == "PLA"
            assert extruder['type']['nozzle_diameter'] == 0.6
        elif extruder['index'] == 1:
            assert extruder['material']['type'] == "ABS"
            assert extruder['type']['nozzle_diameter'] == 0.4
        else:
            assert False
    assert received_events[1]['name'] == 'jobs_updated'
    assert received_events[1]['args'] == [None]
    assert received_events[2]['name'] == 'job_progress_updated'
    assert received_events[2]['args'][0] == {
        "id": 1,
        "name": "test",
        "file_name": "test",
        "progress": 100.0,
        "estimated_seconds_left": 0.0
    }
    assert received_events[3]['name'] == 'jobs_updated'
    assert received_events[3]['args'] == [None]

    received_events = socketio_printer.get_received("/printer")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'job_recovered'
    assert received_events[0]['args'][0]['id'] == 1
    assert received_events[0]['args'][0]['name'] == "test"
    assert isinstance(received_events[0]['args'][0]['started_at'], str)
    assert received_events[0]['args'][0]['interrupted'] is True

    printer = db_manager.get_printers(id=1)

    for extruder in printer.extruders:
        if extruder.index == 0:
            assert extruder.material.type == "PLA"
            assert extruder.type.nozzleDiameter == 0.6
        elif extruder.index == 1:
            assert extruder.material.type == "ABS"
            assert extruder.type.nozzleDiameter == 0.4
        else:
            assert False


def test_on_state_updated(socketio_printer, printer_session_key, db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)
    db_manager.enqueue_created_job(job)

    state_data = {
        "session_key": printer_session_key,
        "state": "Ready"
    }

    printer = db_manager.get_printers(id=1)

    assert printer.state.stateString == "Offline"

    socketio_printer.emit("state_updated", state_data, namespace="/printer")

    received_events = socketio_printer.get_received("/client")

    assert len(received_events) == 2
    assert received_events[0]['name'] == 'printer_data_updated'
    assert received_events[0]['args'][0]['state']['string'] == "Ready"
    assert received_events[1]['name'] == 'jobs_updated'
    assert received_events[1]['args'] == [None]

    received_events = socketio_printer.get_received("/printer")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'print_job'
    assert received_events[0]['args'][0]['id'] == 1
    assert received_events[0]['args'][0]['name'] == "test"
    assert received_events[0]['args'][0]['file_id'] == 1

    printer = db_manager.get_printers(id=1)

    assert printer.state.stateString == "Ready"
    assert printer.current_job.id == job.id


def test_on_extruders_updated(socketio_printer, printer_session_key, db_manager):
    initial_data = {
        "session_key": printer_session_key,
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

    printer = db_manager.get_printers(id=1)
    db_manager.update_printer(printer, idState=db_manager.printer_state_ids["Ready"])

    socketio_printer.emit("extruders_updated", initial_data, namespace="/printer")

    received_events = socketio_printer.get_received("/client")

    assert len(received_events) == 2
    assert received_events[0]['name'] == 'printer_data_updated'
    for extruder in received_events[0]['args'][0]['extruders']:
        if extruder['index'] == 0:
            assert extruder['material']['type'] == "PLA"
            assert extruder['type']['nozzle_diameter'] == 0.6
        elif extruder['index'] == 1:
            assert extruder['material']['type'] == "ABS"
            assert extruder['type']['nozzle_diameter'] == 0.4
        else:
            assert False
    assert received_events[1]['name'] == 'jobs_updated'
    assert received_events[1]['args'] == [None]

    printer = db_manager.get_printers(id=1)

    for extruder in printer.extruders:
        if extruder.index == 0:
            assert extruder.material.type == "PLA"
            assert extruder.type.nozzleDiameter == 0.6
        elif extruder.index == 1:
            assert extruder.material.type == "ABS"
            assert extruder.type.nozzleDiameter == 0.4
        else:
            assert False


def test_on_print_started(socketio_printer, printer_session_key, db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)
    printer = db_manager.get_printers(id=1)
    db_manager.enqueue_created_job(job)
    db_manager.update_job(job, canBePrinted=True)
    db_manager.assign_job_to_printer(printer, job)

    job_data = {
        "session_key": printer_session_key,
        "job_id": job.id,
    }

    socketio_printer.emit("print_started", job_data, namespace="/printer")

    received_events = socketio_printer.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'jobs_updated'
    assert received_events[0]['args'] == [None]

    job = db_manager.get_jobs(id=job.id)

    assert job.state.stateString == "Printing"


def test_on_print_finished(socketio_printer, printer_session_key, db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)
    printer = db_manager.get_printers(id=1)
    db_manager.enqueue_created_job(job)
    db_manager.update_job(job, canBePrinted=True)
    db_manager.assign_job_to_printer(printer, job)
    db_manager.set_printing_job(job)

    job_data = {
        "session_key": printer_session_key,
        "job_id": job.id,
        "cancelled": True,
    }

    socketio_printer.emit("print_finished", job_data, namespace="/printer")

    received_events = socketio_printer.get_received("/client")

    assert len(received_events) == 2
    assert received_events[0]['name'] == 'job_progress_updated'
    assert received_events[0]['args'][0] == {
        "id": job.id,
        'name': 'test',
        'file_name': 'test',
        'progress': 100.0,
        'estimated_seconds_left': 0.0,
    }
    assert received_events[1]['name'] == 'jobs_updated'
    assert received_events[1]['args'] == [None]

    job = db_manager.get_jobs(id=job.id)

    assert job.state.stateString == "Finished"
    assert job.interrupted is True


def test_on_print_feedback(socketio_printer, printer_session_key, db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)
    printer = db_manager.get_printers(id=1)
    db_manager.enqueue_created_job(job)
    db_manager.update_job(job, canBePrinted=True)
    db_manager.assign_job_to_printer(printer, job)
    db_manager.set_printing_job(job)
    db_manager.set_finished_job(job)

    feedback_data = {
        "session_key": printer_session_key,
        "job_id": job.id,
        "feedback_data": {
            "success": True,
            "max_priority": None,
            "printing_sec": 112.1
        }
    }

    socketio_printer.emit("print_feedback", feedback_data, namespace="/printer")

    received_events = socketio_printer.get_received("/client")

    assert len(received_events) == 2
    assert received_events[0]['name'] == 'printer_data_updated'
    assert received_events[0]['args'][0]['total_success_prints'] == 1
    assert received_events[0]['args'][0]['total_failed_prints'] == 0
    assert received_events[0]['args'][0]['total_printing_seconds'] > 0
    assert received_events[1]['name'] == 'jobs_updated'
    assert received_events[1]['args'] == [None]

    job = db_manager.get_jobs(id=feedback_data["job_id"])

    assert job.state.stateString == "Done"


def test_on_printer_temperatures_updated(socketio_printer, printer_session_key, db_manager):
    temp_data = {
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
    data_to_send = temp_data.copy()
    data_to_send["session_key"] = printer_session_key

    socketio_printer.emit("printer_temperatures_updated", data_to_send, namespace="/printer")

    received_events = socketio_printer.get_received("/client")

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'printer_temperatures_updated'
    assert received_events[0]['args'][0] == temp_data


def test_on_job_progress_updated(socketio_printer, printer_session_key, db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)
    printer = db_manager.get_printers(id=1)
    db_manager.enqueue_created_job(job)
    db_manager.update_job(job, canBePrinted=True)
    db_manager.assign_job_to_printer(printer, job)
    db_manager.set_printing_job(job)

    progress_data = {
        "id": 1,
        "progress": 1.2,
        "estimated_seconds_left": 61.1
    }

    data_to_send = progress_data.copy()
    data_to_send["session_key"] = printer_session_key

    socketio_printer.emit("job_progress_updated", data_to_send, namespace="/printer")

    received_events = socketio_printer.get_received("/client")

    expected_progress_data = progress_data.copy()
    expected_progress_data["name"] = "test"
    expected_progress_data["file_name"] = "test"

    assert len(received_events) == 1
    assert received_events[0]['name'] == 'job_progress_updated'
    assert received_events[0]['args'][0] == expected_progress_data

    job = db_manager.get_jobs(id=1)
    assert job.progress == progress_data["progress"]
    assert job.estimatedTimeLeft == timedelta(seconds=progress_data["estimated_seconds_left"])
