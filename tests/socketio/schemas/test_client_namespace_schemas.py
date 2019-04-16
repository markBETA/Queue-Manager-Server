"""
This module implements the printer namespace related marshmallow schemas testing.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from datetime import timedelta

from queuemanager.socketio.schemas import (
    EmitJobAnalyzeDoneSchema, EmitJobAnalyzeErrorSchema, EmitJobEnqueueDoneSchema, EmitJobEnqueueErrorSchema,
    EmitPrinterDataUpdatedSchema, EmitPrinterTemperaturesUpdatedSchema, EmitJobProgressUpdatedSchema,
    EmitJobStartedSchema, EmitJobDoneSchema, OnAnalyzeJob, OnEnqueueJob, EmitAnalyzeErrorHelper,
    EmitEnqueueErrorHelper, EmitPrinterTemperaturesUpdatedHelper
)


def test_emit_job_analyze_done_schema(db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    dump_result = EmitJobAnalyzeDoneSchema().dump(job)

    assert len(dump_result.errors) == 0

    data_to_emit = dump_result.data

    assert data_to_emit == {"id": 1, "name": "test"}


def test_emit_job_analyze_error_schema(db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    helper = EmitAnalyzeErrorHelper(job, "This is a test message", {"job_id": ['Not a valid integer.']})
    dump_result = EmitJobAnalyzeErrorSchema().dump(helper.__dict__)

    assert len(dump_result.errors) == 0

    data_to_emit = dump_result.data

    assert data_to_emit == {
        "job": {"id": 1, "name": "test"},
        "message": "This is a test message",
        "additional_info": {"job_id": ['Not a valid integer.']}
    }


def test_emit_job_enqueue_done_schema(db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    dump_result = EmitJobEnqueueDoneSchema().dump(job)

    assert len(dump_result.errors) == 0

    data_to_emit = dump_result.data

    assert data_to_emit == {"id": 1, "name": "test"}


def test_emit_job_enqueue_error_schema(db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    helper = EmitEnqueueErrorHelper(job, "This is a test message")
    dump_result = EmitJobEnqueueErrorSchema().dump(helper.__dict__)

    assert len(dump_result.errors) == 0

    data_to_emit = dump_result.data

    assert data_to_emit == {
        "job": {"id": 1, "name": "test"},
        "message": "This is a test message",
        "additional_info": None
    }


def test_emit_printer_data_updated_schema(db_manager):
    printer = db_manager.get_printers(id=1)
    material = db_manager.get_printer_materials(id=1)
    extruder_type = db_manager.get_printer_extruder_types(id=4)
    db_manager.update_printer_extruder(printer.extruders[1], material=material, type=extruder_type)

    dump_result = EmitPrinterDataUpdatedSchema().dump(printer)

    assert len(dump_result.errors) == 0

    data_to_emit = dump_result.data

    del data_to_emit["registered_at"]

    assert data_to_emit == {
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


def test_emit_printer_temperatures_updated_schema(db_manager):
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

    helper = EmitPrinterTemperaturesUpdatedHelper(55.1, extruders_temp)
    dump_result = EmitPrinterTemperaturesUpdatedSchema().dump(helper.__dict__)

    assert len(dump_result.errors) == 0

    data_to_emit = dump_result.data

    assert data_to_emit == {
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


def test_emit_job_progress_updated_schema(db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test-file", "/home/Marc/test")
    job = db_manager.insert_job("test-job", file, user)
    job.progress = 1.2
    job.estimatedTimeLeft = timedelta(seconds=61.1)
    dump_result = EmitJobProgressUpdatedSchema().dump(job)

    assert len(dump_result.errors) == 0

    data_to_emit = dump_result.data

    assert data_to_emit == {
        "id": 1,
        "name": "test-job",
        "file_name": "test-file",
        "progress": 1.2,
        "estimated_seconds_left": 61.1
    }


def test_emit_job_started_schema(db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    dump_result = EmitJobStartedSchema().dump(job)

    assert len(dump_result.errors) == 0

    data_to_emit = dump_result.data

    assert data_to_emit == {"id": 1, "name": "test"}


def test_emit_job_done_schema(db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    dump_result = EmitJobDoneSchema().dump(job)

    assert len(dump_result.errors) == 0

    data_to_emit = dump_result.data

    assert data_to_emit == {"id": 1, "name": "test"}


def test_on_analyze_job_schema(db_manager):
    initial_data = {
        "job_id": 1,
    }

    load_result = OnAnalyzeJob().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    assert processed_initial_data["job_id"] == 1

    initial_data["job_id"] = "fail"

    load_result = OnAnalyzeJob().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["job_id"] == ['Not a valid integer.']

    del initial_data["job_id"]

    load_result = OnAnalyzeJob().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["job_id"] == ['Missing data for required field.']
    

def test_on_enqueue_job_schema(db_manager):
    initial_data = {
        "job_id": 1,
    }

    load_result = OnEnqueueJob().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    assert processed_initial_data["job_id"] == 1

    initial_data["job_id"] = "fail"

    load_result = OnEnqueueJob().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["job_id"] == ['Not a valid integer.']

    del initial_data["job_id"]

    load_result = OnEnqueueJob().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["job_id"] == ['Missing data for required field.']
