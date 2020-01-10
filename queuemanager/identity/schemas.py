"""
This module defines the identity header management schemas
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from marshmallow import Schema, fields


class UserIdentityHeader(Schema):
    """ Schema of the user identity header data """
    type = fields.String(required=True, validate=lambda data: data == "user")
    id = fields.Integer(required=True)
    is_admin = fields.Boolean(required=True)


class PrinterIdentityHeader(Schema):
    """ Schema of the printer identity header data """
    type = fields.String(required=True, validate=lambda data: data == "printer")
    id = fields.Integer(required=True)
    serial_number = fields.String(required=True)
