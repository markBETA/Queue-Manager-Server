from datetime import datetime
from marshmallow import fields
from flask_marshmallow import Marshmallow
from sqlalchemy.event import listens_for
from queuemanager.db import db
from .Job import JobSchema
from .Extruder import ExtruderSchema

ma = Marshmallow()

extruders = db.Table("queue_extruders",
    db.Column("extruder_id", db.Integer, db.ForeignKey("extruders.id"), primary_key=True),
    db.Column("queue_id", db.Integer, db.ForeignKey("queues.id"), primary_key=True)
)


class Queue(db.Model):
    """
    Definition of the table queues that contains all prints
    """
    __tablename__ = "queues"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(256), unique=True, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime(), onupdate=datetime.now)
    used_extruders = db.relationship("Extruder", secondary=extruders)
    jobs = db.relationship("Job", backref="queue")


class QueueSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    created_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    updated_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    used_extruders = fields.Nested(ExtruderSchema, many=True)
    jobs = fields.Nested(JobSchema, many=True)


@listens_for(Queue.__table__, "after_create")
def insert_initial_values(*args, **kwargs):
    db.session.add(Queue(name="active", active=True))
    db.session.add(Queue(name="waiting", active=False))

    db.session.commit()
