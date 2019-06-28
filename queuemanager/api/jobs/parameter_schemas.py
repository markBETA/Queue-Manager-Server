"""
This module defines the all the api parameters schemas of the jobs namespace
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.2"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from marshmallow import Schema, fields

from ..definitions import JobStateField


class GetJobsSchema(Schema):
    """ Schema of the parameters accepted by the GET /jobs api resource """
    id = fields.Integer(validate=lambda id: id > 0)
    state = JobStateField(validate=lambda state: state is not None, attribute="idState")
    file_id = fields.Integer(validate=lambda id: id > 0, attribute="idFile")
    user_id = fields.Integer(validate=lambda id: id > 0, attribute="idUser")
    name = fields.String()
    can_be_printed = fields.Boolean(attribute="canBePrinted")
    order_by_priority = fields.Boolean(missing=False)


class GetJobsNotDoneSchema(Schema):
    """ Schema of the parameters accepted by the GET /jobs/not_done api resource """
    order_by_priority = fields.Boolean(missing=False)


class DeleteJobSchema(Schema):
    """ Schema of the parameters accepted by the DELETE /jobs/<job_id> api resource """
    delete_file = fields.Boolean(missing=True)
