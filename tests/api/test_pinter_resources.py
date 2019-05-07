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

from queuemanager.api.printer.models import printer_model


def test_get_printer_resource(db_manager, http_client):
    printer = db_manager.get_printers(id=1)

    r = http_client.get("/api/printer")
    assert r.status_code == 200
    assert r.json == marshal(printer, printer_model)
