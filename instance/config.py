"""
Config file of the Flask App.
"""

import os


class Config(object):
    DEBUG = int(os.getenv("DEBUG", 0))
    ENV = "development"
    TESTING = False

    SQLALCHEMY_BINDS = {
        'app': 'postgresql+psycopg2://postgres:dev@postgres.dev.server/app'
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = (DEBUG >= 2)

    RESTPLUS_VALIDATE = True
    SWAGGER_UI_DOC_EXPANSION = 'list'

    FILE_MANAGER_UPLOAD_DIR = './uploaded_files/'

    SOCKETIO_MESSAGE_QUEUE = "redis://redis.dev.server:6379/1"

    IDENTITY_HEADER = "X-Identity"
    AUTHORIZATION_SUBREQUEST_URL = "http://localhost:5001/"
    AUTHORIZATION_SUBREQUEST_ENDPOINT = "/api/general/check_access_token"
    AUTHORIZATION_SUBREQUEST_METHOD = "POST"

    CORS_ALLOWED_ORIGINS = None
