"""
This module defines the all the API resources for the files namespace.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask import send_file, current_app, make_response
from flask_restplus import Resource, marshal

from .definitions import api
from .models import (
    file_model
)
from ...identity import identity_mgr
from ...database import db_mgr as db
from ...file_storage import file_mgr


@api.route("/<int:file_id>")
class File(Resource):
    """
    /files/<file_id>
    """
    @staticmethod
    def _get_file_development(file):
        """
        Read and send the file attached with the response
        """
        file_d = file_mgr.get_file_d(file)

        return send_file(file_d, as_attachment=True, attachment_filename=file.name)

    @staticmethod
    def _get_file_production(file):
        """
        Make an internal redirection to the file resource
        """
        response = make_response()
        response.headers['X-Accel-Redirect'] = '/files/{}'.format(str(file.id))
        response.headers['Content-Type'] = 'application/octet-stream'
        response.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(file.name)

        return response

    @api.doc(id="get_file")
    @api.doc(security="printer_identity")
    @api.response(200, "Success")
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "Can't find any file with this ID in the database")
    @api.response(422, "Invalid identity")
    @api.response(500, "Unable to read the data from the database")
    @api.response(500, "Unable to retrieve the file from the filesystem")
    @identity_mgr.identity_required()
    def get(self, file_id: int):
        """
        Returns the file with id=file_id or make an internal redirection to the file resource
        (depends on the environment)
        """
        current_printer = identity_mgr.get_identity()

        if current_printer['type'] != "printer":
            return {'message': 'Only printers are allowed to this API resource.'}, 422

        file = db.get_files(id=file_id)
        if not file:
            return {"message": "Can't find any file with this ID in the database."}, 404

        can_access_file = False
        for job in file.jobs:
            if job.assigned_printer.id == current_printer["id"]:
                can_access_file = True
                break

        if not can_access_file:
            return {'message': "This printer can't access to the requested file."}, 401

        if current_app.config.get("ENV") == "production":
            return self._get_file_production(file)
        else:
            return self._get_file_development(file)


@api.route("/<int:file_id>/info")
class FileInfo(Resource):
    """
    /files/<file_id>/info
    """
    @api.doc(id="get_file_info")
    @api.doc(security="printer_identity")
    @api.response(200, "Success", file_model)
    @api.response(401, "Unauthorized resource access")
    @api.response(404, "Can't find any file with this ID in the database")
    @api.response(422, "Invalid identity")
    @api.response(500, "Unable to read the data from the database")
    @identity_mgr.identity_required()
    def get(self, file_id: int):
        """
        Returns the file information with id=file_id
        """
        current_printer = identity_mgr.get_identity()

        if current_printer['type'] != "printer":
            return {'message': 'Only printers are allowed to this API resource.'}, 422

        file = db.get_files(id=file_id)
        if not file:
            return {"message": "Can't find any file with this ID in the database."}, 404

        can_access_file = False
        for job in file.jobs:
            if job.assigned_printer.id == current_printer["id"]:
                can_access_file = True
                break

        if not can_access_file:
            return {'message': "This printer can't access to the requested file."}, 401

        return marshal(file, file_model, skip_none=True), 200
