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
    EmitPrintJobSchema, OnInitialDataSchema, OnStateUpdatedSchema, OnExtrudersUpdatedSchema, OnPrintStartedSchema,
    OnPrintFinishedSchema, OnPrintFeedbackSchema, OnPrinterTemperaturesUpdatedSchema, OnJobProgressUpdatedSchema
)


def test_emit_print_job_schema(db_manager):
    user = db_manager.get_users(id=1)
    file = db_manager.insert_file(user, "test", "/home/Marc/test")
    job = db_manager.insert_job("test", file, user)

    dump_result = EmitPrintJobSchema().dump(job)

    assert len(dump_result.errors) == 0

    data_to_emit = dump_result.data

    assert data_to_emit == {"id": 1, "name": "test", "file_id": 1}


def test_on_initial_data_schema(db_manager):
    initial_data = {
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

    load_result = OnInitialDataSchema().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    assert processed_initial_data["state"] == "Ready"

    for extruder in processed_initial_data["extruders_info"]:
        if extruder["index"] == 0:
            assert extruder["material"].type == "PLA"
            assert extruder["extruder_type"].nozzleDiameter == 0.6
        elif extruder["index"] == 1:
            assert extruder["material"].type == "ABS"
            assert extruder["extruder_type"].nozzleDiameter == 0.4
        else:
            assert False

    initial_data["state"] = "fail"

    load_result = OnInitialDataSchema().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    assert processed_initial_data["state"] == "Unknown"

    initial_data["extruders_info"][0] = {
        "material_type": "fail",
        "extruder_nozzle_diameter": 1.6,
        "index": 0
    }

    load_result = OnInitialDataSchema().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    for extruder in processed_initial_data["extruders_info"]:
        if extruder["index"] == 0:
            assert extruder["material"] is None
            assert extruder["extruder_type"] is None
        elif extruder["index"] == 1:
            assert extruder["material"].type == "ABS"
            assert extruder["extruder_type"].nozzleDiameter == 0.4
        else:
            assert False

    del initial_data["state"]

    load_result = OnInitialDataSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["state"] == ['Missing data for required field.']


def test_on_state_updated_schema(db_manager):
    initial_data = {
        "state": "Ready",
    }

    load_result = OnStateUpdatedSchema().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    assert processed_initial_data["state"] == "Ready"

    initial_data["state"] = "fail"

    load_result = OnStateUpdatedSchema().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    assert processed_initial_data["state"] == "Unknown"

    del initial_data["state"]

    load_result = OnStateUpdatedSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["state"] == ['Missing data for required field.']


def test_on_extruders_updated_schema(db_manager):
    initial_data = {
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

    load_result = OnExtrudersUpdatedSchema().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    for extruder in processed_initial_data["extruders_info"]:
        if extruder["index"] == 0:
            assert extruder["material"].type == "PLA"
            assert extruder["extruder_type"].nozzleDiameter == 0.6
        elif extruder["index"] == 1:
            assert extruder["material"].type == "ABS"
            assert extruder["extruder_type"].nozzleDiameter == 0.4
        else:
            assert False

    initial_data["extruders_info"][0] = {
        "material_type": "fail",
        "extruder_nozzle_diameter": 1.6,
        "index": 0
    }

    load_result = OnExtrudersUpdatedSchema().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    for extruder in processed_initial_data["extruders_info"]:
        if extruder["index"] == 0:
            assert extruder["material"] is None
            assert extruder["extruder_type"] is None
        elif extruder["index"] == 1:
            assert extruder["material"].type == "ABS"
            assert extruder["extruder_type"].nozzleDiameter == 0.4
        else:
            assert False

    initial_data["extruders_info"][0] = {
        "material_type": "fail",
        "extruder_nozzle_diameter": "fail",
        "index": 0
    }

    initial_data["extruders_info"][1] = {
        "material_type": 0.0,
        "extruder_nozzle_diameter": 0.0,
        "index": 0
    }

    load_result = OnExtrudersUpdatedSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors['extruders_info'][0]["extruder_nozzle_diameter"] == ['Not a valid number.']
    assert load_result.errors['extruders_info'][1]["material_type"] == ['Not a valid string.']

    del initial_data["extruders_info"][0]["material_type"]

    load_result = OnExtrudersUpdatedSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors['extruders_info'][0]["material_type"] == ['Missing data for required field.']


def test_on_print_started(db_manager):
    initial_data = {
        "job_id": 1,
    }

    load_result = OnPrintStartedSchema().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    assert processed_initial_data["job_id"] == 1

    initial_data["job_id"] = "fail"

    load_result = OnPrintStartedSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["job_id"] == ['Not a valid integer.']

    del initial_data["job_id"]

    load_result = OnPrintStartedSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["job_id"] == ['Missing data for required field.']


def test_on_print_finished(db_manager):
    initial_data = {
        "job_id": 1,
    }

    load_result = OnPrintFinishedSchema().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    assert processed_initial_data["job_id"] == 1

    initial_data["job_id"] = "fail"

    load_result = OnPrintFinishedSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["job_id"] == ['Not a valid integer.']

    del initial_data["job_id"]

    load_result = OnPrintFinishedSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["job_id"] == ['Missing data for required field.']


def test_on_print_feedback(db_manager):
    initial_data = {
        "job_id": 1,
        "feedback_data": {
            "success": True,
            "max_priority": None,
            "printing_sec": 112.1
        }
    }

    load_result = OnPrintFeedbackSchema().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    assert processed_initial_data["job_id"] == 1
    assert processed_initial_data["feedback_data"]["success"] is True
    assert processed_initial_data["feedback_data"]["max_priority"] is None
    assert processed_initial_data["feedback_data"]["printing_time"] == timedelta(seconds=112.1)

    initial_data["feedback_data"]["printing_sec"] = "fail"

    load_result = OnPrintFeedbackSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["feedback_data"]["printing_sec"] == ['Not a valid number.']

    initial_data["feedback_data"]["printing_sec"] = 112.1
    initial_data["job_id"] = "fail"

    load_result = OnPrintFeedbackSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["job_id"] == ['Not a valid integer.']

    del initial_data["job_id"]

    load_result = OnPrintFeedbackSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["job_id"] == ['Missing data for required field.']


def test_on_printer_temperatures_updated_schema(db_manager):
    initial_data = {
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

    load_result = OnPrinterTemperaturesUpdatedSchema().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    assert processed_initial_data["bed_temp"] == 55.1

    for extruder in processed_initial_data["extruders_temp"]:
        if extruder["index"] == 0:
            assert extruder["temp_value"] == 24.3
        elif extruder["index"] == 1:
            assert extruder["temp_value"] == 215.7

    initial_data["bed_temp"] = "fail"

    load_result = OnPrinterTemperaturesUpdatedSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["bed_temp"] == ['Not a valid number.']

    initial_data["bed_temp"] = 55.1
    initial_data["extruders_temp"][0]["temp_value"] = "fail"

    load_result = OnPrinterTemperaturesUpdatedSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["extruders_temp"][0]["temp_value"] == ['Not a valid number.']


def test_on_job_progress_updated_schema(db_manager):
    initial_data = {
        "id": 1,
        "progress": 1.2,
        "estimated_seconds_left": 61.1
    }

    load_result = OnJobProgressUpdatedSchema().load(initial_data)

    assert len(load_result.errors) == 0

    processed_initial_data = load_result.data

    assert processed_initial_data["id"] == 1
    assert processed_initial_data["progress"] == 1.2
    assert processed_initial_data["estimated_time_left"] == timedelta(seconds=61.1)

    initial_data["progress"] = "fail"

    load_result = OnJobProgressUpdatedSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["progress"] == ['Not a valid number.']

    del initial_data["progress"]
    initial_data["estimated_seconds_left"] = "fail"

    load_result = OnJobProgressUpdatedSchema().load(initial_data)

    assert len(load_result.errors) == 1
    assert load_result.errors["estimated_seconds_left"] == ['Not a valid number.']
