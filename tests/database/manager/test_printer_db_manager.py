"""
This module implements the file data related database models testing.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"


from datetime import timedelta

from queuemanager.database.initial_values import (
    printer_model_initial_values, printer_state_initial_values, printer_extruder_type_initial_values,
    printer_material_initial_values, printer_extruder_initial_values, printer_initial_values
)


def test_printer_models_db_manager(db_manager):
    expected_printer_models = printer_model_initial_values()
    
    for i in range(len(expected_printer_models)):
        expected_printer_models[i].id = i + 1
        
    printer_models = db_manager.get_printer_models()
    
    assert len(expected_printer_models) == len(printer_models)
    
    for i in range(len(expected_printer_models)):
        assert expected_printer_models[i].id == printer_models[i].id
        assert expected_printer_models[i].name == printer_models[i].name
        assert expected_printer_models[i].width == printer_models[i].width
        assert expected_printer_models[i].depth == printer_models[i].depth
        assert expected_printer_models[i].height == printer_models[i].height
        
    sigma_printer_model = db_manager.get_printer_models(name="Sigma")
    assert sigma_printer_model.name == "Sigma"


def test_printer_states_db_manager(db_manager):
    expected_printer_states = printer_state_initial_values()

    for i in range(len(expected_printer_states)):
        expected_printer_states[i].id = i + 1

    printer_states = db_manager.get_printer_states()

    assert len(expected_printer_states) == len(printer_states)

    for i in range(len(expected_printer_states)):
        assert expected_printer_states[i].id == printer_states[i].id
        assert expected_printer_states[i].stateString == printer_states[i].stateString
        assert expected_printer_states[i].isOperationalState == printer_states[i].isOperationalState

    ready_printer_state = db_manager.get_printer_states(stateString="Ready")
    assert ready_printer_state.stateString == "Ready"

    expected_operational_printer_states = []

    for printer_state in expected_printer_states:
        if printer_state.isOperationalState:
            expected_operational_printer_states.append(printer_state)
            
    operational_printer_states = db_manager.get_printer_states(isOperationalState=True)

    assert len(expected_operational_printer_states) == len(operational_printer_states)
    
    for i in range(len(expected_operational_printer_states)):
        assert expected_operational_printer_states[i].id == operational_printer_states[i].id
        assert expected_operational_printer_states[i].stateString == operational_printer_states[i].stateString
        assert expected_operational_printer_states[i].isOperationalState == operational_printer_states[i].isOperationalState


def test_printer_extruder_types_db_manager(db_manager):
    expected_printer_extruder_types = printer_extruder_type_initial_values()

    for i in range(len(expected_printer_extruder_types)):
        expected_printer_extruder_types[i].id = i + 1

    printer_extruder_types = db_manager.get_printer_extruder_types()

    assert len(expected_printer_extruder_types) == len(printer_extruder_types)

    for i in range(len(expected_printer_extruder_types)):
        assert expected_printer_extruder_types[i].id == printer_extruder_types[i].id
        assert expected_printer_extruder_types[i].brand == printer_extruder_types[i].brand
        assert expected_printer_extruder_types[i].nozzleDiameter == printer_extruder_types[i].nozzleDiameter

    e3d_04_printer_extruder_type = db_manager.get_printer_extruder_types(brand="E3D", nozzleDiameter=0.4)
    assert e3d_04_printer_extruder_type[0].brand == "E3D"
    assert e3d_04_printer_extruder_type[0].nozzleDiameter == 0.4
    
    
def test_printer_materials_db_manager(db_manager):
    expected_printer_materials = printer_material_initial_values()

    for i in range(len(expected_printer_materials)):
        expected_printer_materials[i].id = i + 1

    printer_materials = db_manager.get_printer_materials()

    assert len(expected_printer_materials) == len(printer_materials)

    for i in range(len(expected_printer_materials)):
        assert expected_printer_materials[i].id == printer_materials[i].id
        assert expected_printer_materials[i].type == printer_materials[i].type
        assert expected_printer_materials[i].color == printer_materials[i].color
        assert expected_printer_materials[i].brand == printer_materials[i].brand
        assert expected_printer_materials[i].GUID == printer_materials[i].GUID
        assert expected_printer_materials[i].printTemp == printer_materials[i].printTemp
        assert expected_printer_materials[i].bedTemp == printer_materials[i].bedTemp

    pla_printer_material = db_manager.get_printer_materials(type="PLA")
    assert pla_printer_material[0].type == "PLA"


def test_printer_extruders_db_manager(db_manager):
    expected_printer_extruders = printer_extruder_initial_values()

    for i in range(len(expected_printer_extruders)):
        expected_printer_extruders[i].id = i + 1

    printer_extruders = db_manager.get_printer_extruders()

    assert len(expected_printer_extruders) == len(printer_extruders)

    for i in range(len(expected_printer_extruders)):
        assert expected_printer_extruders[i].id == printer_extruders[i].id
        assert expected_printer_extruders[i].idPrinter == printer_extruders[i].idPrinter
        assert expected_printer_extruders[i].idExtruderType == printer_extruders[i].idExtruderType
        assert expected_printer_extruders[i].idMaterial == printer_extruders[i].idMaterial
        assert expected_printer_extruders[i].index == printer_extruders[i].index

    for i in range(len(expected_printer_extruders)):
        expected_printer_extruders[i].idExtruderType = 1
        expected_printer_extruders[i].idMaterial = 1
        db_manager.update_printer_extruder(printer_extruders[i], idExtruderType=1, idMaterial=1)

    printer_extruders = db_manager.get_printer_extruders(idPrinter=1)

    assert len(expected_printer_extruders) == len(printer_extruders)

    for i in range(len(expected_printer_extruders)):
        assert expected_printer_extruders[i].id == printer_extruders[i].id
        assert expected_printer_extruders[i].idPrinter == printer_extruders[i].idPrinter
        assert expected_printer_extruders[i].idExtruderType == printer_extruders[i].idExtruderType
        assert expected_printer_extruders[i].idMaterial == printer_extruders[i].idMaterial
        assert expected_printer_extruders[i].index == printer_extruders[i].index


def test_printer_db_manager(db_manager):
    expected_printers = printer_initial_values()

    for i in range(len(expected_printers)):
        expected_printers[i].id = i + 1

    printers = db_manager.get_printers()

    assert len(expected_printers) == len(printers)

    for i in range(len(expected_printers)):
        assert expected_printers[i].id == printers[i].id
        assert expected_printers[i].idModel == printers[i].idModel
        assert expected_printers[i].idState == printers[i].idState
        assert expected_printers[i].name == printers[i].name
        assert expected_printers[i].serialNumber == printers[i].serialNumber
        assert expected_printers[i].ipAddress == printers[i].ipAddress
        assert expected_printers[i].apiKey == printers[i].apiKey
        assert printers[i].totalSuccessPrints == 0
        assert printers[i].totalFailedPrints == 0
        assert printers[i].totalPrintingTime == timedelta()

    for i in range(len(expected_printers)):
        expected_printers[i].ipAddress = "127.0.0.1"
        db_manager.update_printer(printers[i], ipAddress="127.0.0.1")

    default_printer = db_manager.get_printers(name="default")
    assert default_printer.id == printers[0].id
    assert default_printer.idModel == printers[0].idModel
    assert default_printer.idState == printers[0].idState
    assert default_printer.name == printers[0].name
    assert default_printer.serialNumber == printers[0].serialNumber
    assert default_printer.ipAddress == printers[0].ipAddress
    assert default_printer.apiKey == printers[0].apiKey
    assert default_printer.totalSuccessPrints == printers[0].totalSuccessPrints
    assert default_printer.totalFailedPrints == printers[0].totalFailedPrints
    assert default_printer.totalPrintingTime == printers[0].totalPrintingTime

    db_manager.add_finished_print(default_printer, True, timedelta(hours=3, minutes=10, seconds=30))

    default_printer = db_manager.get_printers(name="default")

    assert default_printer.totalSuccessPrints == 1
    assert default_printer.totalFailedPrints == 0
    assert default_printer.totalPrintingTime == timedelta(hours=3, minutes=10, seconds=30)

    db_manager.add_finished_print(default_printer, False, timedelta(hours=3, minutes=10, seconds=29))

    default_printer = db_manager.get_printers(name="default")

    assert default_printer.totalSuccessPrints == 1
    assert default_printer.totalFailedPrints == 1
    assert default_printer.totalPrintingTime == timedelta(hours=6, minutes=20, seconds=59)
