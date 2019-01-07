from marshmallow import fields
from flask_marshmallow import Marshmallow
from sqlalchemy import UniqueConstraint
from sqlalchemy.event import listens_for
from queuemanager.db import db

ma = Marshmallow()


class Extruder(db.Model):
    """
    Definition of the table extruders that contains all extruders
    """
    __tablename__ = "extruders"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    index = db.Column(db.Integer, nullable=False)
    nozzle_diameter = db.Column(db.Float, nullable=False)
    brand = db.Column(db.String(256), default="e3D")
    loaded_material = db.Column(db.String(256))

    __table_args__ = (UniqueConstraint("index", "nozzle_diameter", "brand"),)

    # def __eq__(self, other):
    #     return self.index == other.index and self.nozzle_diameter == other.nozzle_diameter


class ExtruderSchema(ma.Schema):
    id = fields.Integer()
    index = fields.Integer()
    nozzle_diameter = fields.Float()
    brand = fields.String()
    loaded_material = fields.String()


@listens_for(Extruder.__table__, "after_create")
def insert_initial_values(*args, **kwargs):
    db.session.add(Extruder(nozzle_diameter=0.3, index=0))
    db.session.add(Extruder(nozzle_diameter=0.3, index=1))
    db.session.add(Extruder(nozzle_diameter=0.4, index=0))
    db.session.add(Extruder(nozzle_diameter=0.4, index=1))
    db.session.add(Extruder(nozzle_diameter=0.5, index=0))
    db.session.add(Extruder(nozzle_diameter=0.5, index=1))
    db.session.add(Extruder(nozzle_diameter=0.6, index=0))
    db.session.add(Extruder(nozzle_diameter=0.6, index=1))
    db.session.add(Extruder(nozzle_diameter=0.8, index=0))
    db.session.add(Extruder(nozzle_diameter=0.8, index=1))
    db.session.add(Extruder(nozzle_diameter=1.0, index=0))
    db.session.add(Extruder(nozzle_diameter=1.0, index=1))

    db.session.commit()
