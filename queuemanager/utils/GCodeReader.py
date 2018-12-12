from werkzeug.datastructures import FileStorage
import re


def get_values(gcode_file: FileStorage):
    gcode = gcode_file.stream.read()
    rtime = re.findall(b"(?<=;TIME:)\d*", gcode)
    time = int(rtime[0])
    rfilament = re.findall(b"(?<=;Filament used: )(.*)(?=m)", gcode)
    filament = float(rfilament[0])
    rextruders = re.findall(b"(?<=;Extruders used: )(.*)(?=\\r)", gcode)
    extruders = rextruders[0].decode("utf-8")
    return time, filament, extruders



"""
;TIME:8166
;Filament used: 2.06452m
;Extruders used: T0 0.6
"""

