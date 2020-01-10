import pytest

from ..manager import IdentityManager
from ... import create_app


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    enabled_modules = {
        "identity-mgr"
    }
    app = create_app(__name__, testing=True, enabled_modules=enabled_modules)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='function')
def identity_mgr(app):
    return IdentityManager(app)
