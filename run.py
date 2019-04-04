"""
This file implements the way to run the server from the
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from queuemanager import create_app
from queuemanager.socketio import socketio

if __name__ == "__main__":
    app = create_app(__name__, init_db_static_values=True)
    socketio.run(app, debug=True, host='0.0.0.0')
