"""
This module defines the all the api resources for the jobs namespace.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .definitions import api
from .models import (
    job_state_model, job_allowed_extruder_model, job_allowed_material_model, job_model, job_extruder_model,
    reorder_job_model, edit_job_model
)
from .resources import (
    Jobs, Job, JobCreate, JobStates, JobReorder, JobReprint
)
