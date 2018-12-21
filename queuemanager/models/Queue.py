from datetime import datetime
from marshmallow import fields
from flask_marshmallow import Marshmallow
from queuemanager.db import db
from .Job import JobSchema

ma = Marshmallow()


class Queue(db.Model):
    """
    Definition of the table queues that contains all prints
    """
    __tablename__ = "queues"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(256), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime(), onupdate=datetime.now)
    used_extruders = db.Column(db.PickleType)
    # jobs = db.relationship("Job", backref="queue")


class QueueSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    created_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    updated_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    used_extruders = fields.Dict()
    # jobs = fields.Nested(JobSchema, many=True)

