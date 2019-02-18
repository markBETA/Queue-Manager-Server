import os
from werkzeug.datastructures import FileStorage
from queuemanager.utils import GCodeReader

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
    }
}


def test_gcode_reader():
    path = "input_gcodes"
    for gcode in os.listdir(path):
        with open(os.path.join(path, gcode), "rb") as gcode_file:
            file = FileStorage(stream=gcode_file)
            time, filament, extruders = GCodeReader.get_values(file)
            assert RESULTS[gcode]["time"] == time
            assert RESULTS[gcode]["filament"] == filament
            assert RESULTS[gcode]["extruders"] == extruders
