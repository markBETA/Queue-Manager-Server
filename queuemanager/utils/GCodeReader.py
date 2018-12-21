from werkzeug.datastructures import FileStorage
import re
import tempfile


def get_values(gcode_file: FileStorage):
    gcode = gcode_file.read()
    time_match = re.search(b"(?<=;TIME:)\d*", gcode)
    time = int(time_match.group()) if time_match else None
    filament_match = re.search(b"(?<=;Filament used: )\d*\.?\d*", gcode)
    filament = float(filament_match.group()) if filament_match else None
    extruders_match = re.search(b"(?<=;Extruders used: )(.*)", gcode)
    if extruders_match:
        extruders = {}
        for match in re.finditer(b"(?<=T)[0-9\s.]*", extruders_match.group()):
            key, value = match.group().split()
            extruders[key.decode("utf-8")] = value.decode("utf-8")
    else:
        extruders = None

    return time, filament, extruders
