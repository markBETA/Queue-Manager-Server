"""
This module implements the database structure and the model classes. Also implements
the database initializers.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .definitions import db_conn as db
from .models import (
    File, JobState, JobAllowedMaterial, JobAllowedExtruder, Job, PrinterModel, PrinterState,
    PrinterExtruderType, PrinterMaterial, PrinterExtruder, Printer, User
)
from .listeners import (
    printer_material_initial_values, printer_state_initial_values, printer_extruder_type_initial_values,
    printer_model_initial_values, printer_extruder_initial_values, printer_initial_values,
    user_initial_values, job_state_initial_values
)
from .manager import (
    DBManager, DBManagerError, InvalidParameter, DBInternalError, UniqueConstraintError
)
from flask import current_app
from flask.cli import with_appcontext
import click


########################
# DATABASE INITIALIZER #
########################

def init_db():
    """Clear existing data and create new tables."""
    with current_app.app_context():
        db.drop_all()
        db.create_all()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Register the 'init-db' command to use it with the Flask command interface"""
    init_db()
    click.echo('Database created successfully.')


def init_app(app):
    """Initializes the app context for the database operation."""
    db.init_app(app)
    app.cli.add_command(init_db_command)


####################
# DATABASE MANAGER #
####################

db_mgr = DBManager()
