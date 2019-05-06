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


def test_get_printer_resource(http_client):
    rv = http_client.get("/api/printer")
    assert rv.status_code == 200
    received_data = rv.json
    del received_data['registered_at']
    assert rv.json == {
        'id': 1,
        'name': 'default',
        'model': {
            'id': 2,
            'name': 'Sigmax',
            'width': 420.0,
            'depth': 297.0,
            'height': 210.0
        },
        'state': {
            'id': 1,
            'string': 'Offline',
            'is_operational_state': False
        },
        'extruders': [
            {'index': 0},
            {'index': 1}
        ],
        'serial_number': '020.180622.3180',
        'ip_address': None,
        'total_success_prints': 0,
        'total_failed_prints': 0,
        'total_printing_seconds': 0.0,
        'current_job': {}
    }