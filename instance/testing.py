"""
Testing config file of the Flask App.
"""

from .config import Config as _Config


class Config(_Config):
    TESTING = True

    SQLALCHEMY_BINDS = {
        'app': 'postgresql+psycopg2://postgres:dev@postgres.dev.server/app_test'
    }

    TOKEN_BLACKLIST_REDIS_DB = 9

    FILE_MANAGER_UPLOAD_DIR = './files/'

    JWT_SECRET_KEY = 'super-secret'
    JWT_ALGORITHM = 'HS256'
