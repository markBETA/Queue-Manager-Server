from datetime import datetime
from marshmallow import fields
from flask_marshmallow import Marshmallow
from sqlalchemy.util.langhelpers import symbol
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
    printing = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    file_id = db.Column(db.Integer, db.ForeignKey("files.id"))
    queue_id = db.Column(db.Integer, db.ForeignKey("queues.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def update_helper(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class JobSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    order = fields.Integer()
    printing = fields.Boolean()
    created_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    updated_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    file = fields.Nested(FileSchema)
    user = fields.Nested(UserSchema)


@listens_for(Job.order, "set")
def handle_order(target, value, oldvalue, initiator):
    if oldvalue is symbol("NO_VALUE") or not target.queue:
        return
    if oldvalue > value:
        Job.query.filter(target.queue.id == Job.queue_id, Job.id != target.id, Job.order >= value,
                                 Job.order < oldvalue).update({Job.order: Job.order + 1})
    elif oldvalue < target.order:
        Job.query.filter(target.queue.id == Job.queue_id, Job.id != target.id, Job.order <= value,
                         Job.order > oldvalue).update({Job.order: Job.order - 1})
