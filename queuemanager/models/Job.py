from datetime import datetime
from marshmallow import fields
from flask_marshmallow import Marshmallow
from queuemanager.db import db

ma = Marshmallow()


class Job(db.Model):
    """
    Definition of the table Prints that contains all prints
    """
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(256), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime(), onupdate=datetime.now)
    file_id = db.Column(db.Integer, db.ForeignKey("files.id"))

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class JobSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    created_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    updated_at = fields.DateTime('%d-%m-%YT%H:%M:%S')