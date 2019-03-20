from datetime import datetime
from marshmallow import fields
from flask_marshmallow import Marshmallow
from sqlalchemy import func
from sqlalchemy.event import listens_for
from queuemanager.db import db
from .Job import JobSchema, Job
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
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    used_extruders = db.relationship("Extruder", secondary=extruders, order_by="Extruder.index")
    jobs = db.relationship("Job", backref="queue", order_by="Job.order")


class QueueSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    active = fields.Boolean()
    created_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    updated_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    used_extruders = fields.Nested(ExtruderSchema, many=True)
    jobs = fields.Nested(JobSchema, many=True)


@listens_for(Queue.__table__, "after_create")
def insert_initial_values(*args, **kwargs):
    db.session.add(Queue(name="active", active=True))
    db.session.add(Queue(name="waiting", active=False))

    db.session.commit()


@listens_for(Queue.used_extruders, "bulk_replace")
def handle_extruders_update(target, values, initiatior):
    if target.active:
        jobs_to_waiting_queue = []
        for job in target.jobs:
            # for extruder in job.file.used_extruders:
            #     if extruder not in values:
            #         jobs_to_waiting_queue.append(job)
            #         break
            if set(job.file.used_extruders) != set(values):
                jobs_to_waiting_queue.append(job)
        for job in jobs_to_waiting_queue:
            target.jobs.remove(job)

        waiting_queue = Queue.query.filter_by(active=False).first()
        jobs_to_active_queue = []
        for job in waiting_queue.jobs:
            # for extruder in job.file.used_extruders:
            #     if extruder not in values:
            #         break
            if set(job.file.used_extruders) <= set(values):
                jobs_to_active_queue.append(job)
        for job in jobs_to_active_queue:
            waiting_queue.jobs.remove(job)

        waiting_queue.jobs += jobs_to_waiting_queue
        target.jobs += jobs_to_active_queue

        db.session.commit()


@listens_for(Queue.jobs, "append")
def handle_jobs_append(target, value, initiator):
    max_order = db.session.query(func.max(Job.order)).filter(target.id == Job.queue_id).one()[0]
    if max_order is None:
        value.order = 1
    else:
        value.order = max_order + 1


@listens_for(Queue.jobs, "remove")
def handle_jobs_remove(target, value, initiator):
    Job.query.filter(target.id == Job.queue_id, Job.order > value.order).update({Job.order: Job.order - 1})
