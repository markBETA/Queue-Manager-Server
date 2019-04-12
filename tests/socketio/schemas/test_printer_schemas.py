"""
This module implements the printer data related marshmallow schemas testing.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"


from queuemanager.socketio.schemas import (
    PrinterModelSchema, PrinterStateSchema, PrinterExtruderTypeSchema,
    PrinterMaterialSchema, PrinterExtruderSchema, PrinterSchema
)


def test_printer_model_schema(db_manager):
    expected_serialized_keys = PrinterModelSchema.__dict__['_declared_fields'].keys()

    printer_models = db_manager.get_printer_models()

    serialized_data = PrinterModelSchema().dump(printer_models, many=True).data

    for serialized_model in serialized_data:
        assert expected_serialized_keys == serialized_model.keys()

    assert len(PrinterModelSchema().validate(serialized_data, many=True, partial=True).keys()) == 0


def test_printer_state_schema(db_manager):
    expected_serialized_keys = PrinterStateSchema.__dict__['_declared_fields'].keys()

    printer_states = db_manager.get_printer_states()

    serialized_data = PrinterStateSchema().dump(printer_states, many=True).data

    for serialized_model in serialized_data:
        assert expected_serialized_keys == serialized_model.keys()

    assert len(PrinterStateSchema().validate(serialized_data, many=True, partial=True).keys()) == 0


def test_printer_extruder_type_schema(db_manager):
    expected_serialized_keys = PrinterExtruderTypeSchema.__dict__['_declared_fields'].keys()

    printer_extruder_types = db_manager.get_printer_extruder_types()

    serialized_data = PrinterExtruderTypeSchema().dump(printer_extruder_types, many=True).data

    for serialized_model in serialized_data:
        assert expected_serialized_keys == serialized_model.keys()

    assert len(PrinterExtruderTypeSchema().validate(serialized_data, many=True, partial=True).keys()) == 0


def test_printer_material_schema(db_manager):
    expected_serialized_keys = PrinterMaterialSchema.__dict__['_declared_fields'].keys()

    printer_materials = db_manager.get_printer_materials()

    serialized_data = PrinterMaterialSchema(many=True).dump(printer_materials).data

    for serialized_model in serialized_data:
        assert expected_serialized_keys == serialized_model.keys()

    assert len(PrinterMaterialSchema(many=True).validate(serialized_data).keys()) == 0


def test_printer_extruder_schema(db_manager):
    expected_serialized_keys = PrinterExtruderSchema.__dict__['_declared_fields'].keys()

    printer_extruders = db_manager.get_printer_extruders()

    serialized_data = PrinterExtruderSchema(many=True).dump(printer_extruders).data

    for serialized_model in serialized_data:
        assert expected_serialized_keys == serialized_model.keys()

    assert len(PrinterExtruderSchema(many=True).validate(serialized_data).keys()) == 0


def test_printer_schema(db_manager):
    expected_serialized_keys = PrinterSchema.__dict__['_declared_fields'].keys()

    printers = db_manager.get_printers()

    serialized_data = PrinterSchema(many=True).dump(printers).data

    for serialized_model in serialized_data:
        assert expected_serialized_keys == serialized_model.keys()

    assert len(PrinterSchema(many=True).validate(serialized_data).keys()) == 0
