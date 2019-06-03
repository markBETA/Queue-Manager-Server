"""
This module implements the printer data related database models testing.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from ... import (
    PrinterModel, PrinterState, PrinterExtruderType, PrinterMaterial, PrinterExtruder, Printer
)
from ... import (
    printer_model_initial_values, printer_state_initial_values, printer_extruder_type_initial_values,
    printer_material_initial_values, printer_extruder_initial_values, printer_initial_values
)


def add_printer(session):
    model = PrinterModel.query.first()
    state = PrinterState.query.first()

    printer = Printer(
        name="test-printer",
        idModel=model.id,
        idState=state.id,
        serialNumber="000.00000.000",
        apiKey="8848930e-ad3a-4f05-9151-2c004233470f"
    )

    session.add(printer)
    session.commit()

    return printer


def add_printer_extruders(session, printer):
    extruder_type = PrinterExtruderType.query.first()
    material = PrinterMaterial.query.first()

    printer_extruders = [
        PrinterExtruder(
            idPrinter=printer.id,
            idExtruderType=extruder_type.id,
            idMaterial=material.id,
            index=0
        ),
        PrinterExtruder(
            idPrinter=printer.id,
            idExtruderType=extruder_type.id,
            idMaterial=material.id,
            index=1
        )
    ]

    for extruder in printer_extruders:
        session.add(extruder)
    session.commit()

    return printer_extruders


def test_printer_model_model(session):
    expected_printer_models = printer_model_initial_values()

    for i in range(len(expected_printer_models)):
        expected_printer_models[i].id = i + 1

    printer_models = PrinterModel.query.all()

    str(printer_models)

    assert len(expected_printer_models) == len(printer_models)

    for i in range(len(expected_printer_models)):
        assert expected_printer_models[i].id == printer_models[i].id
        assert expected_printer_models[i].name == printer_models[i].name
        assert expected_printer_models[i].width == printer_models[i].width
        assert expected_printer_models[i].depth == printer_models[i].depth
        assert expected_printer_models[i].height == printer_models[i].height


def test_printer_state_model(session):
    expected_printer_states = printer_state_initial_values()

    for i in range(len(expected_printer_states)):
        expected_printer_states[i].id = i + 1

    printer_states = PrinterState.query.all()

    str(printer_states)

    assert len(expected_printer_states) == len(printer_states)

    for i in range(len(expected_printer_states)):
        assert expected_printer_states[i].id == printer_states[i].id
        assert expected_printer_states[i].stateString == printer_states[i].stateString
        assert expected_printer_states[i].isOperationalState == printer_states[i].isOperationalState


def test_printer_extruder_type_model(session):
    expected_printer_extruder_types = printer_extruder_type_initial_values()

    for i in range(len(expected_printer_extruder_types)):
        expected_printer_extruder_types[i].id = i + 1

    printer_extruder_types = PrinterExtruderType.query.all()

    str(printer_extruder_types)

    assert len(expected_printer_extruder_types) == len(printer_extruder_types)

    for i in range(len(expected_printer_extruder_types)):
        assert expected_printer_extruder_types[i].id == printer_extruder_types[i].id
        assert expected_printer_extruder_types[i].brand == printer_extruder_types[i].brand
        assert expected_printer_extruder_types[i].nozzleDiameter == printer_extruder_types[i].nozzleDiameter


def test_printer_material_model(session):
    expected_printer_materials = printer_material_initial_values()

    for i in range(len(expected_printer_materials)):
        expected_printer_materials[i].id = i + 1

    printer_materials = PrinterMaterial.query.all()

    str(printer_materials)

    assert len(expected_printer_materials) == len(printer_materials)

    for i in range(len(expected_printer_materials)):
        assert expected_printer_materials[i].id == printer_materials[i].id
        assert expected_printer_materials[i].type == printer_materials[i].type
        assert expected_printer_materials[i].color == printer_materials[i].color
        assert expected_printer_materials[i].brand == printer_materials[i].brand
        assert expected_printer_materials[i].GUID == printer_materials[i].GUID
        assert expected_printer_materials[i].printTemp == printer_materials[i].printTemp
        assert expected_printer_materials[i].bedTemp == printer_materials[i].bedTemp


def test_printer_extruder_model(session):
    expected_printer_extruders = printer_extruder_initial_values()
    
    for i in range(len(expected_printer_extruders)):
        expected_printer_extruders[i].id = i + 1

    printer_extruders = PrinterExtruder.query.all()

    str(printer_extruders)

    assert len(expected_printer_extruders) == len(printer_extruders)

    for i in range(len(expected_printer_extruders)):
        assert expected_printer_extruders[i].id == printer_extruders[i].id
        assert expected_printer_extruders[i].idPrinter == printer_extruders[i].idPrinter
        assert expected_printer_extruders[i].index == printer_extruders[i].index


def test_printer_model(session):
    expected_printers = printer_initial_values()

    for i in range(len(expected_printers)):
        expected_printers[i].id = i + 1

    printers = Printer.query.all()

    str(printers)

    assert len(expected_printers) == len(printers)

    for i in range(len(expected_printers)):
        assert expected_printers[i].id == printers[i].id
        assert expected_printers[i].idModel == printers[i].idModel
        assert expected_printers[i].idState == printers[i].idState
        assert expected_printers[i].name == printers[i].name
        assert expected_printers[i].serialNumber == printers[i].serialNumber
        assert expected_printers[i].apiKey == printers[i].apiKey
