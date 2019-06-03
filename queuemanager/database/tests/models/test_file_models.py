"""
This module implements the file data related database models testing.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from ... import (
    File
)
from .test_user_models import add_user


def add_file(session, user):
    file = File(
        idUser=user.id,
        name='foo',
        fullPath='foo',
    )

    session.add(file)
    session.commit()

    return file


def test_file_model(session):
    user = add_user(session)
    file = add_file(session, user)

    str(file)

    assert file.id > 0
    assert file.user == user
