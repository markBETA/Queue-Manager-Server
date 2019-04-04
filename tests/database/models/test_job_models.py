"""
This module implements the job data related database models testing.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from queuemanager.database import (
    JobState, JobAllowedMaterial, JobAllowedExtruder, Job, PrinterMaterial, PrinterExtruderType
)
from queuemanager.database import job_state_initial_values
from .test_user_models import add_user
from .test_file_models import add_file


def add_job_allowed_materials(session, job, allowed_materials):
    job_allowed_materials = []
    
    for material in allowed_materials:
        job_allowed_material = JobAllowedMaterial(
            idJob=job.id, 
            idMaterial=material.id,
            extruderIndex=0
        )
        session.add(job_allowed_material)
        job_allowed_materials.append(job_allowed_material)
    
    session.commit()
    
    return job_allowed_materials


def add_job_allowed_extruder_types(session, job, allowed_extruder_types):
    job_allowed_extruder_types = []

    for extruder_type in allowed_extruder_types:
        job_allowed_extruder_type = JobAllowedExtruder(
            idJob=job.id,
            idExtruderType=extruder_type.id,
            extruderIndex=0
        )
        session.add(job_allowed_extruder_type)
        job_allowed_extruder_types.append(job_allowed_extruder_type)

    session.commit()

    return job_allowed_extruder_types


def add_job(session, file, user):
    state = JobState.query.first()

    job = Job(
        idState=state.id,
        idFile=file.id,
        idUser=user.id,
        name="test-job"
    )

    session.add(job)
    session.commit()

    return job


def test_job_state_model(session):
    expected_job_states = job_state_initial_values()

    for i in range(len(expected_job_states)):
        expected_job_states[i].id = i + 1

    job_states = JobState.query.all()

    str(job_states)

    assert len(expected_job_states) == len(job_states)

    for i in range(len(expected_job_states)):
        assert expected_job_states[i].id == job_states[i].id
        assert expected_job_states[i].stateString == job_states[i].stateString


def test_job_allowed_material_model(session):
    user = add_user(session)
    file = add_file(session, user)
    job = add_job(session, file, user)
    allowed_materials = [PrinterMaterial.query.first(), PrinterMaterial.query.first()]
    job_allowed_materials = add_job_allowed_materials(session, job, allowed_materials)

    str(job_allowed_materials)

    assert len(allowed_materials) == len(job_allowed_materials)

    for i in range(len(allowed_materials)):
        assert job_allowed_materials[i].id > 0
        assert job_allowed_materials[i].job == job
        assert job_allowed_materials[i].material == allowed_materials[i]


def test_job_allowed_extruder_type_model(session):
    user = add_user(session)
    file = add_file(session, user)
    job = add_job(session, file, user)
    allowed_extruder_types = [PrinterExtruderType.query.first(), PrinterExtruderType.query.first()]
    job_allowed_extruder_types = add_job_allowed_extruder_types(session, job, allowed_extruder_types)

    str(job_allowed_extruder_types)

    assert len(allowed_extruder_types) == len(job_allowed_extruder_types)

    for i in range(len(allowed_extruder_types)):
        assert job_allowed_extruder_types[i].id > 0
        assert job_allowed_extruder_types[i].job == job
        assert job_allowed_extruder_types[i].type == allowed_extruder_types[i]


def test_job_model(session):
    user = add_user(session)
    file = add_file(session, user)
    job = add_job(session, file, user)

    str(job)

    assert job.id > 0
