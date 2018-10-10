from flask import current_app

from . import socketio


@socketio.on('message')
def handle_message(message):
    current_app.logger.info('received message: ' + message)


@socketio.on('connect')
def connect():
    current_app.logger.info('client connected')


@socketio.on('disconnect')
def disconnect():
    current_app.logger.info('client disconnected')
