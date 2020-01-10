"""
This module sets all the exception handlers of this application
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask import jsonify
from werkzeug.exceptions import HTTPException

from .identity import MissingIdentityHeader, IdentityValidationError
from .database import InvalidParameter, DBManagerError
from .file_storage.exceptions import FileManagerError


def set_exception_handlers(app, from_api=False):
    if not from_api:
        @app.errorhandler(HTTPException)
        def http_exception_handler(e):
            return jsonify({"message": str(e.description)}), e.code

    @app.errorhandler(MissingIdentityHeader)
    def api_error_handler(_e):
        return jsonify({'message': str("Missing Identity Header")}), 401

    @app.errorhandler(IdentityValidationError)
    def api_error_handler(e):
        return jsonify({'message': str(e)}), 422

    @app.errorhandler(InvalidParameter)
    def db_manager_error_handler(e):
        return jsonify({'message': str(e)}), 400

    @app.errorhandler(DBManagerError)
    def db_manager_error_handler(_e):
        return jsonify({'message': 'Unable to read/write data at the database.'}), 500

    @app.errorhandler(FileManagerError)
    def file_manager_error(e):
        return jsonify({'message': str(e)}), 500

    # TODO: Identity error handlers
