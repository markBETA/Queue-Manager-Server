"""
Config file of the Flask App.
"""

import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'queuemanager.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

SWAGGER_UI_DOC_EXPANSION = 'list'

GCODE_STORAGE_PATH = os.path.join(basedir, '../../gcodes')

