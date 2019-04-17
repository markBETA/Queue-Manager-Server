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

from flask_restplus import Resource, marshal

from .definitions import api
from .models import (
    printer_model
)
from ...database import db_mgr as db
from ...database.manager.exceptions import (
    DBManagerError
)


@api.route("")
class Printer(Resource):
    """
    /printer
    """
    @api.doc(id="get_printer")
    @api.response(200, "Success", printer_model)
    @api.response(500, "Unable to read the data from the database")
    def get(self):
        """
        Returns the printer data
        """
        try:
            printer = db.get_printers(id=1)
        except DBManagerError:
            return {'message': 'Unable to read the data from the database'}, 500

        return marshal(printer, printer_model)
