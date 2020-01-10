"""
This module defines the identity header management utils
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

import json
import warnings
import urllib3

from functools import wraps
from json import JSONDecodeError
from flask import request

from flask import _request_ctx_stack as ctx_stack

from .exceptions import (
    MissingIdentityHeader, IdentityValidationError, SubrequestConnectionError, SubrequestTimeoutError,
    SubrequestError, AuthenticationFailed
)
from .schemas import UserIdentityHeader, PrinterIdentityHeader


class IdentityManager(object):
    """
    This class implements the management of the identity header validation and deserialization
    """
    def __init__(self, app=None):
        self.app = None
        self.http = None
        self.config = dict()
        self.user_identity_header_schema = UserIdentityHeader()
        self.printer_identity_header_schema = PrinterIdentityHeader()
        self.get_identity_from_header = True

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

        if (
            'IDENTITY_HEADER' not in app.config
        ):
            warnings.warn(
                'IDENTITY_HEADER not set. '
                'Defaulting IDENTITY_HEADER to "X-Identity".'
            )

        self.config["identity_header"] = app.config.get("IDENTITY_HEADER", "X-Identity")
        self.get_identity_from_header = self.app.config["ENV"] == "production" or self.app.config["TESTING"]
        try:
            self.http = urllib3.connection_from_url(app.config["AUTHORIZATION_SUBREQUEST_URL"])
            self.config["subrequest_endpoint"] = app.config["AUTHORIZATION_SUBREQUEST_ENDPOINT"]
            self.config["subrequest_method"] = app.config["AUTHORIZATION_SUBREQUEST_METHOD"]
        except KeyError as e:
            raise Exception("Missing '{}' identity manager configuration parameter".format(e.args[0]))

    def get_identity_header_json(self, http_request=request):
        identity_header_value = http_request.headers.get(self.config["identity_header"], None)

        # Check if the identity header is present
        if identity_header_value is None:
            raise MissingIdentityHeader()

        # Decode the identity header
        try:
            return json.loads(identity_header_value)
        except JSONDecodeError:
            raise IdentityValidationError("Bad Authorization header. Expected JSON value")

    def set_current_identity(self, identity_data: dict):
        if type(identity_data) != dict:
            raise IdentityValidationError("Bad Authorization header. Expected JSON value")

        # Identify if the identity header corresponds to a printer or user
        identity_type = identity_data.get("type")
        if identity_type == "user":
            deserialized_identity = self.user_identity_header_schema.load(identity_data)
        elif identity_type == "printer":
            deserialized_identity = self.printer_identity_header_schema.load(identity_data)
        else:
            raise IdentityValidationError("Bad Authorization header. Unknown identity type")

        # Check if it has been deserialized successfully and add it to the flask content stack
        if not deserialized_identity.errors:
            ctx_stack.top.identity = deserialized_identity.data
        else:
            raise IdentityValidationError("Bad Authorization header. Invalid format")

    def validate_identity_in_request(self):
        # Retrieve the identity header contents
        identity_data = self.get_identity_header_json()
        self.set_current_identity(identity_data)

    def authentication_subrequest(self):
        # Make a subrequest to an external API to retrieve the identity
        try:
            subrequest_response = self.http.request(
                self.config["subrequest_method"], self.config["subrequest_endpoint"], headers=request.headers
            )
        except urllib3.exceptions.ConnectionError as e:
            raise SubrequestConnectionError(str(e), response=e.response)
        except urllib3.exceptions.HTTPError as e:
            raise SubrequestError(str(e))

        # If the authentication was successful (status code 200)
        if subrequest_response.status == 200:
            # Retrieve the identity header contents
            identity_data = self.get_identity_header_json(subrequest_response)
            self.set_current_identity(identity_data)
        else:
            print("Subrequest response status:", subrequest_response.status)
            raise AuthenticationFailed(response=subrequest_response)

    @staticmethod
    def get_identity():
        """
        In a protected endpoint, this will return the identity of the user or printer that is accessing
        this endpoint. If no identity header is present, and empty dict is returned instead.
        """
        current_identity = getattr(ctx_stack.top, 'identity', None)
        if current_identity is None:
            raise IdentityValidationError()
        else:
            return current_identity

    def identity_required(self):
        def decorator(fn):
            if self.get_identity_from_header:
                @wraps(fn)
                def wrapper(*args, **kwargs):
                    self.current_identity = None
                    self.validate_identity_in_request()
                    return fn(*args, **kwargs)
                return wrapper
            else:
                @wraps(fn)
                def wrapper(*args, **kwargs):
                    self.current_identity = None
                    self.authentication_subrequest()
                    return fn(*args, **kwargs)
                return wrapper
        return decorator
