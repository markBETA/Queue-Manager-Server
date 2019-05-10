"""
This module implements the printer namespace resources test suite.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask_restplus import marshal

from queuemanager.api.printer.models import (
    printer_model, printer_material_model, printer_extruder_type_model
)


def test_get_printer(db_manager, http_client):
    printer = db_manager.get_printers(id=1)

    r = http_client.get("/api/printer")
    assert r.status_code == 200
    assert r.json == marshal(printer, printer_model)


def test_get_printer_materials(db_manager, http_client):
    printer_materials = db_manager.get_printer_materials()

    r = http_client.get("api/printer/materials")
    assert r.status_code == 200
    assert r.json == marshal(printer_materials, printer_material_model, skip_none=True)


def test_get_printer_extruder_types(db_manager, http_client):
    printer_extruder_types = db_manager.get_printer_materials()

    r = http_client.get("api/printer/extruder_types")
    assert r.status_code == 200
    assert r.json == marshal(printer_extruder_types, printer_extruder_type_model, skip_none=True)
