"""
This module defines the all the global variables needed API namespaces
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from flask_restplus import fields
from datetime import timedelta


####################
# GLOBAL FUNCTIONS #
####################

def underscore_to_camel_case(s: str):
    new_s = ""
    i = 0
    while i < len(s):
        if s[i] == "_":
            i += 1
            new_s += s[i].upper()
        else:
            new_s += s[i]
        i += 1

    return new_s


def prepare_database_filters(filters: dict, allowed_filters: set):
    prepared_filters = dict()

    for key, value in filters.items():
        if key in allowed_filters:
            prepared_filters[underscore_to_camel_case(key)] = value
        else:
            raise KeyError("Invalid '{}' filter key".format(key))

    return prepared_filters


#######################
# CUSTOM MODEL FIELDS #
#######################

class TimeField(fields.Raw):
    def format(self, value: timedelta):
        """ Encode a timedelta object to string """
        return value.total_seconds()
