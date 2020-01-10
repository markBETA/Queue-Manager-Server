"""
Testing config file of the Flask App.
"""

from .config import Config as _Config


class Config(_Config):
    TESTING = True

    SQLALCHEMY_BINDS = {
        'app': 'postgresql+psycopg2://postgres:dev@postgres.dev.server/app_test'
    }

    SOCKETIO_MESSAGE_QUEUE = None

    FILE_MANAGER_UPLOAD_DIR = './files/'
