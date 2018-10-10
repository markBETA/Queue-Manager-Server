#!/usr/bin/env bash

db_file="./instance/queuemanager.sqlite" #Database file relative path

## This script can be used to start the flask server automatically in development mode

# Activate the virtual environment
source ./venv/bin/activate
# Set Flask environment
export FLASK_APP=queuemanager
export FLASK_ENV=development
# Check if the database file exists. If it doesn't exist, initialize the db file
if test ! -f "$db_file"
then
    echo "$db_file not found. Creating..."
    flask init-db
fi
# Run Flask application
flask run --host=0.0.0.0