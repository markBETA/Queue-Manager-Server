"""
This module defines the all the api parameters schemas of the jobs namespace
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from marshmallow import Schema, fields

from ...database import db_mgr


class JobStateField(fields.Raw):
    """ Custom field for deserialize the printer state field """
    def _deserialize(self, value, attr, data):
        if value in db_mgr.job_state_ids.keys():
            return db_mgr.job_state_ids[value]
        else:
            return None


class GetJobsSchema(Schema):
    """ Schema of the parameters accepted by the GET /jobs api resource """
    id = fields.Integer(validate=lambda id: id > 0)
    state = JobStateField(validate=lambda state: state in db_mgr.job_state_ids.keys(), attribute="idState")
    file_id = fields.Integer(validate=lambda id: id > 0, attribute="idFile")
    user_id = fields.Integer(validate=lambda id: id > 0, attribute="idUser")
    name = fields.String()
    can_be_printed = fields.Boolean(attribute="canBePrinted")
    order_by_priority = fields.Boolean(default=False)
