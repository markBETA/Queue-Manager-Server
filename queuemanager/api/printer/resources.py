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
    printer_material_model, printer_extruder_type_model
)
from ...database import db_mgr as db
from ...database.manager.exceptions import (
    DBManagerError
)


@api.route("/materials")
class PrinterMaterials(Resource):
    """
    /printer/materials
    """
    @api.doc(id="get_printer_materials")
    @api.response(200, "Success", printer_material_model)
    @api.response(500, "Unable to read the data from the database")
    def get(self):
        """
        Returns the file with id=file_id
        """
        try:
            printer_materials = db.get_printer_materials()
        except DBManagerError:
            return {'message': 'Unable to read the data from the database'}, 500

        return marshal(printer_materials, printer_material_model)


@api.route("/extruder_types")
class PrinterExtruderTypes(Resource):
    """
    /printer/extruder_types
    """
    @api.doc(id="get_printer_extruder_types")
    @api.response(200, "Success", printer_extruder_type_model)
    @api.response(500, "Unable to read the data from the database")
    def get(self):
        """
        Returns the file with id=file_id
        """
        try:
            printer_extruder_types = db.get_printer_extruder_types()
        except DBManagerError:
            return {'message': 'Unable to read the data from the database'}, 500

        return marshal(printer_extruder_types, printer_extruder_type_model)
