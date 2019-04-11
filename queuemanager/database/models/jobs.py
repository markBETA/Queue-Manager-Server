"""
This module implements the jobs data related database models.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from datetime import datetime

from .table_names import (
    JOB_STATES_TABLE, JOB_ALLOWED_MATERIALS_TABLE, JOB_ALLOWED_EXTRUDERS_TABLE, JOB_EXTRUDERS_TABLE,
    JOBS_TABLE, PRINTER_MATERIALS_TABLE, PRINTER_EXTRUDER_TYPES_TABLE, FILES_TABLE, USERS_TABLE
)
from ..definitions import db_conn as db


class JobState(db.Model):
    """
    Definition of the table JOB_STATES_TABLE that contains the job known states.
    """
    __tablename__ = JOB_STATES_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    stateString = db.Column(db.String(256), unique=True, nullable=False)

    jobs = db.relationship('Job', back_populates='state')

    def __repr__(self):
        return '[{}]<id: {} / stateString: {}>'.format(self.__tablename__, self.id, self.stateString)


class JobAllowedMaterial(db.Model):
    """
    Definition of the table JOB_ALLOWED_MATERIALS that contains the job allowed materials.
    """
    __tablename__ = JOB_ALLOWED_MATERIALS_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    idJob = db.Column(db.Integer, db.ForeignKey(JOBS_TABLE+'.id'), nullable=False)
    idMaterial = db.Column(db.Integer, db.ForeignKey(PRINTER_MATERIALS_TABLE+'.id'), nullable=False)
    extruderIndex = db.Column(db.Integer, nullable=False)

    job = db.relationship('Job', back_populates='allowed_materials', uselist=False)
    material = db.relationship('PrinterMaterial', back_populates='jobs', uselist=False)

    def __repr__(self):
        return '[{}]<idJob: {} / idMaterial: {} / extruder_index: {}>'.format(self.__tablename__, self.idJob,
                                                                              self.idMaterial, self.extruderIndex)


class JobAllowedExtruder(db.Model):
    """
    Definition of the table JOB_ALLOWED_EXTRUDERS that contains the job allowed extruder types.
    """
    __tablename__ = JOB_ALLOWED_EXTRUDERS_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    idJob = db.Column(db.Integer, db.ForeignKey(JOBS_TABLE+'.id'), nullable=False)
    idExtruderType = db.Column(db.Integer, db.ForeignKey(PRINTER_EXTRUDER_TYPES_TABLE+'.id'), nullable=False)
    extruderIndex = db.Column(db.Integer, nullable=False)

    job = db.relationship('Job', back_populates='allowed_extruder_types', uselist=False)
    type = db.relationship('PrinterExtruderType', back_populates='jobs', uselist=False)

    def __repr__(self):
        return '[{}]<idJob: {} / idExtruderType: {} / extruder_index: {}>'.format(self.__tablename__, self.idJob,
                                                                                  self.idExtruderType,
                                                                                  self.extruderIndex)


class JobExtruder(db.Model):
    """
    Definition of the table JOB_EXTRUDERS_TABLE that contains the job extruders information
    """
    __tablename__ = JOB_EXTRUDERS_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    idJob = db.Column(db.Integer, db.ForeignKey(JOBS_TABLE + '.id'), nullable=False)
    idUsedExtruderType = db.Column(db.Integer, db.ForeignKey(PRINTER_EXTRUDER_TYPES_TABLE+'.id'))
    idUsedMaterial = db.Column(db.Integer, db.ForeignKey(PRINTER_MATERIALS_TABLE+'.id'))
    estimatedNeededMaterial = db.Column(db.Float, nullable=False, default=0)
    extruderIndex = db.Column(db.Integer, nullable=False)

    job = db.relationship('Job', back_populates='extruders_data', uselist=False)
    used_extruder_type = db.relationship('PrinterExtruderType', uselist=False)
    used_material = db.relationship('PrinterMaterial', uselist=False)

    def __repr__(self):
        return '[{}]<idJob: {} / idUsedExtruderType: {} / idUsedMaterial: {} / estimatedNeededMaterial: {} /' \
               ' extruder_index: {}>'.format(self.__tablename__, self.idJob, self.idUsedExtruderType,
                                             self.idUsedMaterial, self.estimatedNeededMaterial, self.extruderIndex)


class Job(db.Model):
    """
    Definition of the table JOBS_TABLE that contains all jobs of the queue
    """
    __tablename__ = JOBS_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    idState = db.Column(db.Integer, db.ForeignKey(JOB_STATES_TABLE + '.id'), nullable=False)
    idFile = db.Column(db.Integer, db.ForeignKey(FILES_TABLE + '.id'), nullable=False)
    idUser = db.Column(db.Integer, db.ForeignKey(USERS_TABLE + '.id'), nullable=False)
    name = db.Column(db.String(256), unique=True, nullable=False)
    canBePrinted = db.Column(db.Boolean)
    priority_i = db.Column(db.Integer)
    analyzed = db.Column(db.Boolean, default=False)
    createdAt = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updatedAt = db.Column(db.DateTime, onupdate=datetime.now)
    retries = db.Column(db.Integer)
    succeed = db.Column(db.Boolean)

    state = db.relationship('JobState', back_populates='jobs', uselist=False)
    file = db.relationship('File', back_populates='jobs', uselist=False)
    user = db.relationship('User', back_populates='jobs', uselist=False)
    allowed_materials = db.relationship('JobAllowedMaterial', back_populates='job', cascade="all, delete-orphan")
    allowed_extruder_types = db.relationship('JobAllowedExtruder', back_populates='job', cascade="all, delete-orphan")
    extruders_data = db.relationship('JobExtruder', back_populates='job', cascade="all, delete-orphan")

    def __repr__(self):
        return '[{}]<id: {} / name: {} / priority_i: {}>'.format(self.__tablename__, self.id, self.name,
                                                                 self.priority_i)
