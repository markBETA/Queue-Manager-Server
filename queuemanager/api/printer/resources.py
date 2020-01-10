"""
This module defines the all the API resources for the printer namespace.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask_restplus import Resource, marshal

from .definitions import api
from .models import (
    printer_model, printer_material_model, printer_extruder_type_model
)
from ...identity import identity_mgr
from ...database import db_mgr as db


@api.route("")
class Printer(Resource):
    """
    /printer
    """
    @api.doc(id="get_printer")
    @api.doc(security=["user_identity", "printer_identity"])
    @api.response(200, "Success", printer_model)
    @api.response(500, "Unable to read the data from the database")
    @identity_mgr.identity_required()
    def get(self):
        """
        Returns the printer data
        """
        printer = db.get_printers(id=1)

        return marshal(printer, printer_model, skip_none=True)


@api.route("/materials")
class PrinterMaterials(Resource):
    """
    /printer/materials
    """
    @api.doc(id="get_printer_materials")
    @api.doc(security=["user_identity", "printer_identity"])
    @api.response(200, "Success", [printer_material_model])
    @api.response(500, "Unable to read the data from the socketio_printer")
    @identity_mgr.identity_required()
    def get(self):
        """
        Returns all the known printer materials
        """
        printer_materials = db.get_printer_materials()

        return marshal(printer_materials, printer_material_model, skip_none=True), 200


@api.route("/extruder_types")
class PrinterExtruderTypes(Resource):
    """
    /printer/extruder_types
    """
    @api.doc(id="get_printer_extruder_types")
    @api.doc(security=["user_identity", "printer_identity"])
    @api.response(200, "Success", [printer_extruder_type_model])
    @api.response(500, "Unable to read the data from the socketio_printer")
    @identity_mgr.identity_required()
    def get(self):
        """
        Returns all the known printer extruder types
        """
        printer_extruder_types = db.get_printer_extruder_types()

        return marshal(printer_extruder_types, printer_extruder_type_model, skip_none=True), 200
