"""
This module defines the all the global variables needed by the socketio module
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from functools import wraps

from flask import current_app, request, session
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_socketio import SocketIO, disconnect
from jwt.exceptions import PyJWTError

from .manager import SocketIOManager

############################
# SOCKET.IO SERVER MANAGER #
############################

socketio = SocketIO()
socketio_mgr = SocketIOManager()


@socketio.on("connect")
def connected():
    try:
        verify_jwt_in_request()
        current_app.logger.info("Connection with SID '{}' authorized".format(request.sid))
    except (JWTExtendedException, PyJWTError) as e:
        current_app.logger.warning("Connection with SID '{}' authorization failed ({})".format(request.sid, str(e)))
        return False

    session["identity"] = get_jwt_identity()

    return True


##########################################
# RECEIVED EVENT AUTHORIZATION DECORATOR #
##########################################

def socketio_auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Get the session key from the received data
        session_key = args[1].pop('session_key', None)
        current_app.logger.debug("Received session key {} of client '{}'".format(session_key, request.sid))

        # If we didn't received any key, disconnect the client and return
        if session_key is None:
            current_app.logger.warning("Missing session key. Disconnecting client with SID '{}'".format(request.sid))
            disconnect()
            return

        # If the key didn't match the stored one, disconnect the client and return
        if session_key != session.get('key'):
            current_app.logger.warning("Invalid session key (expected: {}). Disconnecting client with SID '{}'".
                                       format(session.get('key'), request.sid))
            disconnect()
            return

        current_app.logger.debug("Session key of client '{}' validated".format(request.sid))
        return fn(*args, **kwargs)

    return wrapper
