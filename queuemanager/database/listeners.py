"""
This module implements the database initializers and the tables population data.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from sqlalchemy.event import listens_for

from .definitions import db_conn as db
from .initial_values import (
    printer_material_initial_values, printer_state_initial_values, printer_extruder_type_initial_values,
    printer_model_initial_values, printer_extruder_initial_values, printer_initial_values,
    user_initial_values, job_state_initial_values
)
from .models import (
    JobState, PrinterModel, PrinterState, PrinterExtruderType, PrinterMaterial, PrinterExtruder,
    Printer, User
)


def _add_rows(row_list):
    for row in row_list:
        db.session.add(row)
    db.session.commit()


############################
# PRINTER TABLES LISTENERS #
############################

@listens_for(PrinterModel.__table__, "after_create")
def insert_initial_values(*_args, **_kwargs):
    _add_rows(printer_model_initial_values())


@listens_for(PrinterState.__table__, "after_create")
def insert_initial_values(*_args, **_kwargs):
    _add_rows(printer_state_initial_values())


@listens_for(PrinterExtruderType.__table__, "after_create")
def insert_initial_values(*_args, **_kwargs):
    _add_rows(printer_extruder_type_initial_values())


@listens_for(PrinterMaterial.__table__, "after_create")
def insert_initial_values(*_args, **_kwargs):
    _add_rows(printer_material_initial_values())


@listens_for(PrinterExtruder.__table__, "after_create")
def insert_initial_values(*_args, **_kwargs):
    _add_rows(printer_extruder_initial_values())


@listens_for(Printer.__table__, "after_create")
def insert_initial_values(*_args, **_kwargs):
    _add_rows(printer_initial_values())


#########################
# USER TABLES LISTENERS #
#########################

@listens_for(User.__table__, "after_create")
def insert_initial_values(*_args, **_kwargs):
    _add_rows(user_initial_values())


#########################
# JOB TABLES LISTENERS #
#########################

@listens_for(JobState.__table__, "after_create")
def insert_initial_values(*_args, **_kwargs):
    _add_rows(job_state_initial_values())
