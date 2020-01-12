"""
This module defines the identity manager related exceptions.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"


class IdentityManagerError(Exception):
    """
    File Manager Exception upper class.
    """
    pass


class IdentityValidationError(IdentityManagerError):
    """
    This exception will be raised on an identity validation error.
    """
    pass


class MissingIdentityHeader(IdentityValidationError):
    """
    This exception will be raised when the identity header is not present.
    """
    pass


class InvalidIdentityHeader(IdentityValidationError):
    """
    This exception will be raised when the identity header has an invalid format.
    """
    pass


class AuthenticationSubrequestError(IdentityManagerError):
    """
    This exception will be raised when the authentication subrequest fails.
    """
    pass


class MissingAuthorizationHeader(AuthenticationSubrequestError):
    """
    This exception will be raised when the identity header is not present.
    """
    pass

class SubrequestError(AuthenticationSubrequestError):
    """
    This exception will be raised when the authentication subrequest reports a HTTP error.
    """
    pass


class AuthenticationFailed(AuthenticationSubrequestError):
    """
    This exception will be raised when the authentication fails from the subrequest.
    """

    def __init__(self, *args, content, code):
        """Initialize `AuthenticationFailed` with `content` and `code` objects."""
        self.content = content.decode('utf-8')
        self.code = code
        super(AuthenticationSubrequestError, self).__init__(*args)
