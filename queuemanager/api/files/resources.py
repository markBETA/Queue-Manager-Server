"""
This module defines the all the api resources for the jobs namespace
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask import send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restplus import Resource, marshal

from .definitions import api
from .models import (
    file_model
)
from ...database import db_mgr as db
from ...file_storage import file_mgr


@api.route("/<int:file_id>")
class File(Resource):
    """
    /files/<file_id>
    """
    @api.doc(id="get_file")
    @api.doc(security="printer_access_jwt")
    @api.response(200, "Success")
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "Can't find any file with this ID in the database")
    @api.response(422, "Invalid access token")
    @api.response(500, "Unable to read the data from the database")
    @api.response(500, "Unable to retrieve the file from the filesystem")
    @jwt_required
    def get(self, file_id: int):
        """
        Returns the file with id=file_id
        """
        current_user = get_jwt_identity()

        if current_user.get('type') != "printer":
            return {'message': 'Only printer access tokens are allowed.'}, 422

        printer_id = current_user.get('id')
        if printer_id is None:
            return {'message': "Can't retrieve the printer ID from the access token."}, 422

        file = db.get_files(id=file_id)
        if not file:
            return {"message": "Can't find any file with this ID in the database."}, 404

        can_access_file = False
        for job in file.jobs:
            if job.assigned_printer.id == printer_id:
                can_access_file = True
                break

        if not can_access_file:
            return {'message': "This printer can't access to the requested file."}, 401

        file_d = file_mgr.get_file_d(file)

        return send_file(file_d, as_attachment=True, attachment_filename=file.name)


@api.route("/<int:file_id>/info")
class File(Resource):
    """
    /files/<file_id>/info
    """
    @api.doc(id="get_file_info")
    @api.doc(security="printer_access_jwt")
    @api.response(200, "Success", file_model)
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "Can't find any file with this ID in the database")
    @api.response(422, "Invalid access token")
    @api.response(500, "Unable to read the data from the database")
    @jwt_required
    def get(self, file_id: int):
        """
        Returns the file information with id=file_id
        """
        current_user = get_jwt_identity()

        if current_user.get('type') != "printer":
            return {'message': 'Only printer access tokens are allowed.'}, 422

        printer_id = current_user.get('id')
        if printer_id is None:
            return {'message': "Can't retrieve the printer ID from the access token."}, 422

        file = db.get_files(id=file_id)
        if not file:
            return {"message": "Can't find any file with this ID in the database."}, 404

        can_access_file = False
        for job in file.jobs:
            if job.assigned_printer.id == printer_id:
                can_access_file = True
                break

        if not can_access_file:
            return {'message': "This printer can't access to the requested file."}, 401

        return marshal(file, file_model, skip_none=True), 200
