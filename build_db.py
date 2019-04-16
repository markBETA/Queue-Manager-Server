"""
This module can build a new database according to the structure defined in the 'database' module.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask import Flask

from queuemanager.database import init_app, init_db

app = Flask(__name__)

app.config.from_pyfile('instance/config.py')


if __name__ == '__main__':
    app.app_context().push()
    init_app(app)
    init_db()
