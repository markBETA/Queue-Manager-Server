"""
This module implements the database structure and the model classes. Also implements
the database initializers.
"""

__author__ = "Eloi Pardo"
__credits__ = ["Eloi Pardo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Eloi Pardo"
__email__ = "epardo@fundaciocim.org"
__status__ = "Development"

from flask import current_app
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
import click


#################################
# SQLALCHEMY CONNECTION MANAGER #
#################################

db = SQLAlchemy()


########################
# DATABASE INITIALIZER #
########################

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Creates new tables."""
    with current_app.app_context():
        db.drop_all()
        db.create_all()
    click.echo('Database created successfully.')


def init_app(app):
    """Initializes the app context for the database operation."""
    db.init_app(app)
    app.cli.add_command(init_db_command)
