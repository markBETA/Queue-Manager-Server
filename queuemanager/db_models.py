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

from datetime import datetime
from flask import current_app
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
import click


#################################
# SQLALCHEMY CONNECTION MANAGER #
#################################

db = SQLAlchemy()
ma = Marshmallow()


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


###############################
# DATABASE MODELS DECLARATION #
###############################

class Print(db.Model):
    """
    Definition of the table Prints that contains all prints
    """
    __tablename__ = "Prints"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)

    def __init__(self, name):
        self.name = name

class PrintSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    created_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
