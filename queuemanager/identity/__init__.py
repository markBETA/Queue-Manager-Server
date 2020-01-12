"""
This module implements the identity header management
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .exceptions import (
    IdentityManagerError, IdentityValidationError, MissingIdentityHeader, IdentityValidationError,
    MissingIdentityHeader, InvalidIdentityHeader, AuthenticationSubrequestError,
    SubrequestConnectionError, SubrequestTimeoutError, SubrequestError, AuthenticationFailed
)
from .definitions import identity_mgr


def init_app(app, *args, **kwargs):
    identity_mgr.init_app(app, *args, **kwargs)
