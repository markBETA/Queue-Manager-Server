"""
Config file of the Flask App.
"""

import os

SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')

OCTOPI_API_KEY = os.getenv('OCTOPI_API_KEY', 'my_octopi_key')

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'queuemanager.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

SWAGGER_UI_DOC_EXPANSION = 'list'

GCODE_STORAGE_PATH = os.path.join(basedir, '../../gcodes')
