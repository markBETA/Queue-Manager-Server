from datetime import datetime
from marshmallow import fields
from flask_marshmallow import Marshmallow
from queuemanager.db import db
from .Extruder import ExtruderSchema

ma = Marshmallow()

extruders = db.Table("file_extruders",
    db.Column("extruder_id", db.Integer, db.ForeignKey("extruders.id"), primary_key=True),
    db.Column("file_id", db.Integer, db.ForeignKey("files.id"), primary_key=True)
)


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
    used_extruders = db.relationship("Extruder", secondary=extruders)
    used_material = db.Column(db.Float)
    jobs = db.relationship("Job", backref="file")


class FileSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    loaded_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    time = fields.Integer()
    used_extruders = fields.Nested(ExtruderSchema, many=True)
    used_material = fields.Float()

