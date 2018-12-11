from datetime import datetime
from marshmallow import fields
from flask_marshmallow import Marshmallow
from queuemanager.db_models import db

ma = Marshmallow()


class File(db.Model):
    """
    Definition of the table Files that contains all files
    """
    __tablename__ = "Files"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(256), unique=True, nullable=False)
    filepath = db.Column(db.String(256), nullable=False)
    loaded_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    prints = db.relationship('Prints', backref="Files", lazy=True)


class FileSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    filepath = fields.String()
    loaded_at = fields.DateTime('%d-%m-%YT%H:%M:%S')