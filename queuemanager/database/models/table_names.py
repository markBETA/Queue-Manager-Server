"""
This module defines the all the table names of the database.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"


##################
# PRINTER TABLES #
##################

PRINTER_MODELS_TABLE = 'printer_known_models'
PRINTER_STATES_TABLE = 'printer_states'
PRINTER_EXTRUDER_TYPES_TABLE = 'printer_extruder_types'
PRINTER_MATERIALS_TABLE = 'printer_materials'
PRINTER_EXTRUDERS_TABLE = 'printer_extruders'
PRINTERS_TABLE = 'printers'


##############
# JOB TABLES #
##############

JOB_STATES_TABLE = 'job_states'
JOB_ALLOWED_MATERIALS_TABLE = 'job_allowed_materials'
JOB_ALLOWED_EXTRUDERS_TABLE = 'job_allowed_extruders'
JOB_EXTRUDERS_TABLE = 'job_extruders'
JOBS_TABLE = 'jobs'


###############
# USER TABLES #
###############

USERS_TABLE = 'users'


###############
# FILE TABLES #
###############

FILES_TABLE = 'files'
