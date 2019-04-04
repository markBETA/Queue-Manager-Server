"""
Config file of the Flask App.
"""

import os

SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')

SQLALCHEMY_DATABASE_URI = 'sqlite:///data/database.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

RESTPLUS_VALIDATE = True
SWAGGER_UI_DOC_EXPANSION = 'list'

FILE_MANAGER_UPLOAD_DIR = './data/files/'
