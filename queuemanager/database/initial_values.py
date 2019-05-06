"""
This module implements the database initializers and the tables population data.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from werkzeug.security import generate_password_hash

from queuemanager.database.models import (
    JobState, PrinterModel, PrinterState, PrinterExtruderType, PrinterMaterial,
    PrinterExtruder, Printer, User
)


#################################
# PRINTER TABLES INITIAL VALUES #
#################################

def printer_model_initial_values():
    return [
        PrinterModel(name="Sigma", width=210.0, depth=297.0, height=210),
        PrinterModel(name="Sigmax", width=420.0, depth=297.0, height=210)
    ]


def printer_state_initial_values():
    return [
        PrinterState(stateString="Offline", isOperationalState=False),
        PrinterState(stateString="Ready", isOperationalState=True),
        PrinterState(stateString="Printing", isOperationalState=True),
        PrinterState(stateString="Paused", isOperationalState=True),
        PrinterState(stateString="Print finished", isOperationalState=True),
        PrinterState(stateString="Busy", isOperationalState=True),
        PrinterState(stateString="Error", isOperationalState=False),
        PrinterState(stateString="Unknown", isOperationalState=False),
    ]


def printer_extruder_type_initial_values():
    return [
        PrinterExtruderType(brand="E3D", nozzleDiameter=0.3),
        PrinterExtruderType(brand="E3D", nozzleDiameter=0.4),
        PrinterExtruderType(brand="E3D", nozzleDiameter=0.5),
        PrinterExtruderType(brand="E3D", nozzleDiameter=0.6),
        PrinterExtruderType(brand="E3D", nozzleDiameter=0.8),
        PrinterExtruderType(brand="E3D", nozzleDiameter=1.0),
    ]


def printer_material_initial_values():
    return [
        PrinterMaterial(type="PLA", printTemp=215.0, bedTemp=65.0),
        PrinterMaterial(type="PVA", printTemp=220.0, bedTemp=60.0),
        PrinterMaterial(type="PET-G", printTemp=235.0, bedTemp=85.0),
        PrinterMaterial(type="ABS", printTemp=260.0, bedTemp=90.0),
        PrinterMaterial(type="Nylon", printTemp=250.0, bedTemp=65.0),
        PrinterMaterial(type="TPU", printTemp=235.0, bedTemp=65.0),

    ]


def printer_extruder_initial_values():
    return [
        PrinterExtruder(idPrinter=1, index=0),
        PrinterExtruder(idPrinter=1, index=1),
    ]


def printer_initial_values():
    return [
        Printer(idModel=2, idState=1, name="default", serialNumber="020.180622.3180",
                apiKey="b82a38ead630438abf1bc56a2c6aa281")
    ]


##############################
# USER TABLES INITIAL VALUES #
##############################

def user_initial_values():
    return [
        User(username="bcn3d", password=generate_password_hash("1234"), isAdmin=True),
    ]


#############################
# JOB TABLES INITIAL VALUES #
#############################

def job_state_initial_values():
    return [
        JobState(stateString="Created"),
        JobState(stateString="Waiting"),
        JobState(stateString="Printing"),
        JobState(stateString="Finished"),
        JobState(stateString="Done"),
        JobState(stateString="Unknown"),
    ]
