"""
Production config file of the Flask App.
"""

import datetime

from .config import Config as _Config


class Config(_Config):
    DEBUG = 0
    ENV = "production"

    SQLALCHEMY_BINDS = {
        'app': 'postgresql+psycopg2://postgres:bcnraprep@queue-manager-database.c8lme8jgnxxk.eu-west-3.rds.amazonaws.com/app',
    }

    FILE_MANAGER_UPLOAD_DIR = '/opt/deployment/files/'

    SOCKETIO_MESSAGE_QUEUE = "redis://queue-manager-cache.4mhe1r.ng.0001.euw3.cache.amazonaws.com:6379/1"

    CORS_ALLOWED_ORIGINS = ["http://queuemanagerbcn3d.ml", "http://www.queuemanagerbcn3d.ml"]
