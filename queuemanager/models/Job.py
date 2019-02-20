from datetime import datetime
from marshmallow import fields
from flask_marshmallow import Marshmallow
from sqlalchemy import func, inspect
from sqlalchemy.event import listens_for
from queuemanager.db import db
from .File import FileSchema
from .User import UserSchema

ma = Marshmallow()


class Job(db.Model):
    """
    Definition of the table Prints that contains all prints
    """
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(256), unique=True, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime(), onupdate=datetime.now)
    file_id = db.Column(db.Integer, db.ForeignKey("files.id"))
    queue_id = db.Column(db.Integer, db.ForeignKey("queues.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def update_helper(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


@listens_for(Job, "before_insert")
def calculate_order(mapper, connection, target):
    max_order = db.session.query(func.max(Job.order)).filter(target.queue.id == Job.queue_id).one()[0]
    if max_order is None:
        target.order = 1
    else:
        target.order = max_order + 1


@listens_for(Job, "before_update")
def handle_order(mapper, connection, target):
    old_order = inspect(target).attrs["order"].history.deleted
    if len(old_order) == 0:
        return
    old_order = old_order[0]
    if old_order > target.order:
        Job.query.filter(target.queue.id == Job.queue_id, Job.id != target.id, Job.order >= target.order,
                         Job.order < old_order).update({Job.order: Job.order + 1})
    elif old_order < target.order:
        Job.query.filter(target.queue.id == Job.queue_id, Job.id != target.id, Job.order <= target.order,
                         Job.order > old_order).update({Job.order: Job.order - 1})


@listens_for(Job, "after_delete")
def handle_deletion(mapper, connection, target):
    Job.query.filter(target.queue.id == Job.queue_id, Job.order > target.order).update({Job.order: Job.order - 1})


class JobSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    order = fields.Integer()
    created_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    updated_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    file = fields.Nested(FileSchema)
    user = fields.Nested(UserSchema)
