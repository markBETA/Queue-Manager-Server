"""
This module defines all helpers used by the events emitted and received by the socket.io namespaces
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"


############################
# CLIENT NAMESPACE HELPERS #
############################

class EmitAnalyzeErrorHelper:
    def __init__(self, job_obj, error_message, additional_info=None):
        self.job = job_obj
        self.message = error_message
        self.additional_info = additional_info


class EmitEnqueueErrorHelper(EmitAnalyzeErrorHelper):
    pass


class EmitPrinterTemperaturesUpdatedHelper:
    def __init__(self,  bed_temp, extruders_temp):
        self.bed_temp = bed_temp
        self.extruders_temp = extruders_temp


class EmitJobProgressUpdatedHelper:
    def __init__(self, job_id, progress, elapsed_time, estimated_time_left):
        self.job_id = job_id
        self.progress = progress
        self.elapsed_time = elapsed_time
        self.estimated_time_left = estimated_time_left

