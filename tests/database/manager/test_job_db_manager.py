"""
This module implements the file data related database models testing.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from queuemanager.database.models import (
    PrinterMaterial, PrinterExtruderType, PrinterState, Job, job_state_initial_values
)
from ..models import (
    add_user, add_file, add_job, add_printer, add_printer_extruders
)


def test_job_states_db_manager(db_manager):
    expected_job_states = job_state_initial_values()

    for i in range(len(expected_job_states)):
        expected_job_states[i].id = i + 1

    job_states = db_manager.get_job_states()

    assert len(expected_job_states) == len(job_states)

    for i in range(len(expected_job_states)):
        assert expected_job_states[i].id == job_states[i].id
        assert expected_job_states[i].stateString == job_states[i].stateString

    waiting_job_state = db_manager.get_job_states(stateString="Waiting")
    assert waiting_job_state.stateString == "Waiting"


def test_job_allowed_materials_db_manager(db_manager):
    session = db_manager.db_session
    user = add_user(session)
    file = add_file(session, user)
    job = add_job(session, file, user)
    printer_materials = PrinterMaterial.query.all()
    job_printer_materials = [
        (printer_materials[0], 0),
        (printer_materials[1], 1),
    ]

    job_allowed_materials = db_manager.insert_job_allowed_materials(job, job_printer_materials)

    assert len(job_printer_materials) == len(job_allowed_materials)

    for i in range(len(job_printer_materials)):
        assert job_allowed_materials[i].idJob == job.id
        assert job_allowed_materials[i].idMaterial == job_printer_materials[i][0].id

    get_job_allowed_materials = db_manager.get_job_allowed_materials(job, 0)

    assert [printer_materials[0]] == get_job_allowed_materials

    get_jobs_by_material = db_manager.get_jobs_by_material(printer_materials[1])

    assert [job] == get_jobs_by_material


def test_job_allowed_extruders_db_manager(db_manager):
    session = db_manager.db_session
    user = add_user(session)
    file = add_file(session, user)
    job = add_job(session, file, user)
    printer_extruder_types = PrinterExtruderType.query.all()
    job_printer_extruder_types = [
        (printer_extruder_types[0], 0),
        (printer_extruder_types[1], 1),
    ]

    job_allowed_extruder_types = db_manager.insert_job_allowed_extruder_types(job, job_printer_extruder_types)

    assert len(job_printer_extruder_types) == len(job_allowed_extruder_types)

    for i in range(len(job_printer_extruder_types)):
        assert job_allowed_extruder_types[i].idJob == job.id
        assert job_allowed_extruder_types[i].idExtruderType == job_printer_extruder_types[i][0].id

    get_job_allowed_extruder_types = db_manager.get_job_allowed_extruder_types(job, 0)

    assert [printer_extruder_types[0]] == get_job_allowed_extruder_types

    get_jobs_by_extruder_type = db_manager.get_jobs_by_extruder_type(printer_extruder_types[1])

    assert [job] == get_jobs_by_extruder_type


def test_job_db_manager(db_manager):
    session = db_manager.db_session
    user = add_user(session)
    file = add_file(session, user)
    printer = add_printer(session)
    printer.state = PrinterState.query.filter_by(stateString="Ready").first()
    session.commit()
    printer_extruders = add_printer_extruders(session, printer)
    printer_materials = PrinterMaterial.query.all()
    printer_extruder_types = PrinterExtruderType.query.all()
    jobs = []

    for i in range(4):
        allowed_materials = [
            (printer_materials[i], 0),
            # (printer_materials[i], 1)
        ]
        allowed_extruder_types = [
            (printer_extruder_types[i], 0),
            (printer_extruder_types[i], 1)
        ]
        job = db_manager.insert_job("test-job-{}".format(str(i)), file, user)
        db_manager.insert_job_allowed_materials(job, allowed_materials)
        db_manager.insert_job_allowed_extruder_types(job, allowed_extruder_types)
        jobs.append(job)

    test_job_0 = db_manager.get_jobs(name="test-job-0")

    assert test_job_0 == jobs[0]

    all_jobs = db_manager.get_jobs(idFile=file.id)

    assert all_jobs == jobs

    updated_job = db_manager.update_job(jobs[0], canBePrinted=False)

    assert [updated_job] == Job.query.filter_by(canBePrinted=False).all()

    for i in range(4):
        job = db_manager.enqueue_created_job(jobs[i])
        assert job.priority_i == i + 1
        assert job.state.stateString == "Waiting"
        assert job.canBePrinted == (i == 0)

    for printer_extruder in printer_extruders:
        printer_extruder.type = printer_extruder_types[1]
        printer_extruder.material = printer_materials[1]

    db_manager.update_can_be_printed_jobs()

    for i in range(4):
        assert jobs[i].canBePrinted == (i == 1)

    first_job_in_queue = db_manager.get_first_job_in_queue()

    assert first_job_in_queue == jobs[1]

    printing_job = db_manager.set_printing_job(first_job_in_queue)

    assert printing_job.state.stateString == "Printing"
    assert printing_job.priority_i is None

    first_job_in_queue = db_manager.get_first_job_in_queue()

    assert first_job_in_queue is None

    finished_job = db_manager.set_finished_job(printing_job)

    assert finished_job.state.stateString == "Finished"

    done_job = db_manager.set_done_job(finished_job)

    assert done_job.state.stateString == "Done"

    created_job = db_manager.update_job(done_job, idState=db_manager.job_state_ids["Created"])
    db_manager.enqueue_created_job(created_job)

    expected_queue_order = [jobs[0], jobs[2], jobs[3], jobs[1]]
    assert expected_queue_order == Job.query.filter(Job.priority_i.isnot(None)).order_by(Job.priority_i.asc()).all()

    expected_queue_order = [jobs[3], jobs[0], jobs[2], jobs[1]]
    db_manager.reorder_job_in_queue(jobs[3], None)
    assert expected_queue_order == Job.query.filter(Job.priority_i.isnot(None)).order_by(Job.priority_i.asc()).all()

    expected_queue_order = [jobs[0], jobs[2], jobs[3], jobs[1]]
    db_manager.reorder_job_in_queue(jobs[3], jobs[2])
    assert expected_queue_order == Job.query.filter(Job.priority_i.isnot(None)).order_by(Job.priority_i.asc()).all()

    expected_queue_order = [jobs[0], jobs[1], jobs[2], jobs[3]]
    db_manager.reorder_job_in_queue(jobs[1], jobs[0])
    assert expected_queue_order == Job.query.filter(Job.priority_i.isnot(None)).order_by(Job.priority_i.asc()).all()

    expected_queue_order = [jobs[0], jobs[2], jobs[1], jobs[3]]
    db_manager.reorder_job_in_queue(jobs[2], jobs[0])
    assert expected_queue_order == Job.query.filter(Job.priority_i.isnot(None)).order_by(Job.priority_i.asc()).all()

    expected_queue_order = [jobs[0], jobs[1], jobs[2], jobs[3]]
    db_manager.reorder_job_in_queue(jobs[2], jobs[1])
    assert expected_queue_order == Job.query.filter(Job.priority_i.isnot(None)).order_by(Job.priority_i.asc()).all()

    printing_job = db_manager.set_printing_job(db_manager.get_first_job_in_queue())
    assert printing_job.state.stateString == "Printing"

    enqueued_job = db_manager.enqueue_printing_or_finished_job(printing_job, max_priority=False)
    assert enqueued_job.state.stateString == "Waiting"

    expected_queue_order = [jobs[0], jobs[2], jobs[3], jobs[1]]
    assert expected_queue_order == Job.query.filter(Job.priority_i.isnot(None)).order_by(Job.priority_i.asc()).all()

    printing_job = db_manager.set_printing_job(db_manager.get_first_job_in_queue())
    assert printing_job.state.stateString == "Printing"

    expected_queue_order = [jobs[0], jobs[2], jobs[3]]
    assert expected_queue_order == Job.query.filter(Job.priority_i.isnot(None)).order_by(Job.priority_i.asc()).all()

    enqueued_job = db_manager.enqueue_printing_or_finished_job(printing_job, max_priority=True)
    assert enqueued_job.state.stateString == "Waiting"

    expected_queue_order = [jobs[1], jobs[0], jobs[2], jobs[3]]
    assert expected_queue_order == Job.query.filter(Job.priority_i.isnot(None)).order_by(Job.priority_i.asc()).all()
