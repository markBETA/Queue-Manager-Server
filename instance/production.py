"""
Production config file of the Flask App.
"""

import datetime

from .config import Config as _Config


class Config(_Config):
    DEBUG = 0
    ENV = "production"

    SQLALCHEMY_BINDS = {
        'app': 'postgresql+psycopg2://postgres:7T#uZqxfL[z%,GGA@queue-manager-database.cdsfc1sk270d.eu-west-1.rds.amazonaws.com/app',
    }

    FILE_MANAGER_UPLOAD_DIR = '/mnt/efs/queuemanager/shared-files/'

    SOCKETIO_MESSAGE_QUEUE = "redis://queue-manager-redis.kklcm3.0001.euw1.cache.amazonaws.com:6379"

    AUTHORIZATION_SUBREQUEST_URL = "http://172.31.29.210:80/"

    CORS_ALLOWED_ORIGINS = ["http://queuemanagerbcn3d.ml", "http://www.queuemanagerbcn3d.ml"]
