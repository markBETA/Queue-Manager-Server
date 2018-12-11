from datetime import datetime
from marshmallow import fields
from flask_marshmallow import Marshmallow
from queuemanager.db_models import db

ma = Marshmallow()


class Print(db.Model):
    """
    Definition of the table Prints that contains all prints
    """
    __tablename__ = "Prints"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(256), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    filepath = db.Column(db.String(256), nullable=False)

    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class PrintSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String()
    created_at = fields.DateTime('%d-%m-%YT%H:%M:%S')
    filepath = fields.String()
