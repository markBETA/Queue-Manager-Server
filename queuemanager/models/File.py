from datetime import datetime
from marshmallow import fields
from flask_marshmallow import Marshmallow
from queuemanager.db import db

ma = Marshmallow()


class File(db.Model):
    """
    Definition of the table Files that contains all prints
    """
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(256), unique=True, nullable=False)
    loaded_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    path = db.Column(db.String(256), unique=True, nullable=False)
    time = db.Column(db.Integer)
    used_extruders = db.Column(db.PickleType)
    used_material = db.Column(db.Float)
    jobs = db.relationship("Job", backref="file")


class FileSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    loaded_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    time = fields.Integer()
    used_extruders = fields.Dict()
    used_material = fields.Float()

