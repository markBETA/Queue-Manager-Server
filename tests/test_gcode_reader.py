import os
from werkzeug.datastructures import FileStorage
from queuemanager.utils import GCodeReader
from tests.globals import GCODES

RESULTS = {
    "S_3DBenchy.gcode": {
        "time": 8166,
        "filament": 2.06452,
        "extruders": {"0": "0.6"}
    },
    "S_3DBenchy_-_Dualprint.gcode": {
        "time": 17415,
        "filament": 2.35445,
        "extruders": {"0": "0.4", "1": "0.6"}
    },
    "S_BMO.gcode": {
        "time": 36259,
        "filament": 12.8955,
        "extruders": {"0": "0.6"}
    },
    "S_1-4_flag.gcode": {
        "time": 3805,
        "filament": 0.934383,
        "extruders": {"0": "0.4"}
    },
    "S_Cilindre.gcode": {
        "time": 296,
        "filament": 0.125224,
        "extruders": {"0": "0.6"}
    },
    "S_Cilindre1.gcode": {
        "time": 290,
        "filament": 0.123397,
        "extruders": {"0": "0.6"}
    }
}


def test_gcode_reader(app):
    with app.app_context():
        path = app.config.get("TEST_INPUTS_PATH")
        for gcode in GCODES:
            with open(os.path.join(path, gcode.get("file_name")), "rb") as gcode_file:
                file = FileStorage(stream=gcode_file)
                time, filament, extruders = GCodeReader.get_values(file)
                assert gcode.get("time") == time
                assert gcode.get("filament") == filament
                assert gcode.get("extruders") == extruders
