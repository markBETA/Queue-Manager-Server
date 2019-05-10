"""
This file implements the way to run the server from the python interpreter
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

import argparse

from queuemanager import create_app

parser = argparse.ArgumentParser(description='Run the queue manager server')
parser.add_argument('--host', type=str, default='0.0.0.0',
                    help='Address where the server is listening for connections (Default: 0.0.0.0)')
parser.add_argument('--port', type=int, default=5000,
                    help='Port where the server is listening for connections (Default: 5000)')


if __name__ == "__main__":
    args = parser.parse_args()
    app = create_app(__name__, init_db_static_values=True)

    from queuemanager.socketio import socketio
    socketio.run(app, debug=(app.config.get("DEBUG") > 0), host=args.host, port=args.port)
