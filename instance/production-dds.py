"""
Production config file of the Flask App for the DDS servers.
"""

from .production import Config as _Config


class Config(_Config):
    SQLALCHEMY_BINDS = {
        'app': 'postgresql+psycopg2://postgres:bcnraprep@queue-manager-database.c8lme8jgnxxk.eu-west-3.rds.amazonaws.com/app_dds',
    }

    REDIS_SERVER_HOST = 'queue-manager-cache.4mhe1r.ng.0001.euw3.cache.amazonaws.com'
    TOKEN_BLACKLIST_REDIS_DB = 2

    SOCKETIO_MESSAGE_QUEUE = "redis://queue-manager-cache.4mhe1r.ng.0001.euw3.cache.amazonaws.com:6379/3"

    CORS_ALLOWED_ORIGINS = ["http://dds.queuemanagerbcn3d.ml"]
