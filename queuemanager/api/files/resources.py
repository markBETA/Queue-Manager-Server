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
from flask_restplus import Resource

from .definitions import api
from ...database import db_mgr as db
from ...database.manager.exceptions import (
    DBManagerError
)
from ...file_storage import file_mgr
from ...file_storage.exceptions import (
    FileManagerError
)


@api.route("/<int:file_id>")
class File(Resource):
    """
    /files/<file_id>
    """
    @api.doc(id="get_file")
    @api.response(200, "Success")
    @api.response(404, "Can't find any file with this ID in the database")
    @api.response(500, "Unable to read the data from the database")
    @api.response(500, "Unable to retrieve the file from the filesystem")
    def get(self, file_id: int):
        """
        Returns the file with id=file_id
        """
        try:
            file = db.get_files(id=file_id)
            if not file:
                return {"message": "Can't find any file with this ID in the database"}, 404
        except DBManagerError:
            return {'message': 'Unable to read the data from the database'}, 500

        try:
            file_d = file_mgr.get_file_d(file)
        except FileManagerError:
            return {'message': 'Unable to retrieve the file from the filesystem'}, 500

        return send_file(file_d, as_attachment=True, attachment_filename=file.name)
