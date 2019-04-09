"""
This module defines the file storage manager class
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

import json
import math
import os
import uuid
import warnings
from datetime import timedelta

from flask import current_app
from werkzeug.utils import secure_filename

from .exceptions import (
    InvalidFileHeader, MissingHeaderKeys, InvalidFileType, FilesystemError, InvalidFileInformation
)
from ..database import (
    DBManager, User, File, Job
)


class FileManager(object):
    """
    This class implements the interface for save and retrieve files from the filesystem
    """
    def __init__(self, db_manager: DBManager, app=None, file_header_prefix=";PrintInfo/",
                 file_header_end="/PrintInfo\n"):
        self.db_manager = db_manager
        self.app = None
        self.file_header_prefix = file_header_prefix
        self.file_header_end = file_header_end
        self.upload_dir = None

        if app is not None:
            self.init_app(app)

    def _create_upload_dir(self):
        os.makedirs(self.app.config.get('FILE_MANAGER_UPLOAD_DIR'), exist_ok=True)

    def _get_allowed_materials_and_extruder_types(self, file: File):
        # Prepare the allowed materials and extruder types data
        allowed_materials = []
        allowed_extruder_types = []

        for i in range(len(list(file.fileInformation["extruders"]))):
            extruder = dict(file.fileInformation["extruders"][i])
            if bool(extruder["active"]):
                # Get all the materials in the database of this type
                materials_of_this_type = \
                    self.db_manager.get_printer_materials(type=str(extruder["material"]["type"]))
                for material in materials_of_this_type:
                    allowed_materials.append((material, i))
                # Get all the extruder types in the database of this nozzle diameter
                extruders_of_this_size = \
                    self.db_manager.get_printer_extruder_types(nozzleDiameter=float(extruder["nozzle_size"]))
                for extruder_type in extruders_of_this_size:
                    allowed_extruder_types.append((extruder_type, i))

        return allowed_materials, allowed_extruder_types

    @staticmethod
    def _calculate_weight_from_filament_distance(extruded_filament_distance, filament_diameter: float = 2.85,
                                                 filament_density: float = 1.25):
        return math.pi * ((filament_diameter / 2.0) ** 2) * filament_density * extruded_filament_distance

    def _get_file_print_information(self, file: File):
        # Prepare the fields to modify at the file object
        fields_to_update = {}

        # Get the estimated printing time from the header
        estimated_printing_time = float(file.fileInformation["print_times"]["total"])
        fields_to_update["estimatedPrintingTime"] = timedelta(seconds=estimated_printing_time)

        # Calculate the estimated needed material for all the extruders
        weight = 0.0
        for extruder in file.fileInformation["extruders"]:
            filament_diameter = float(extruder["material"]["diameter"])
            filament_density = float(extruder["material"]["density"])
            extruded_filament_distance = float(extruder["material_used"])
            weight += self._calculate_weight_from_filament_distance(extruded_filament_distance, filament_diameter,
                                                                    filament_density)

        fields_to_update["estimatedNeededMaterial"] = weight

        return fields_to_update

    def _identify_file_info(self, line: str, file: File):
        line_elements = line.split(":")
        if len(line_elements) == 2:
            if line_elements[0].lower() == "time":
                estimated_printing_time = timedelta(seconds=float(line_elements[1].strip()))
                self.db_manager.update_file(file, estimatedPrintingTime=estimated_printing_time)
            elif line_elements[0].lower() == "filament used":
                estimated_needed_material = \
                    self._calculate_weight_from_filament_distance(float(line_elements[1].strip()[:-1]))
                self.db_manager.update_file(file, estimatedNeededMaterial=estimated_needed_material)

    def init_app(self, app):
        self.app = app

        if (
            'FILE_MANAGER_UPLOAD_DIR' not in app.config
        ):
            warnings.warn(
                'FILE_MANAGER_UPLOAD_DIR not set. '
                'Defaulting FILE_MANAGER_UPLOAD_DIR to "./upload_folder/".'
            )

        self.upload_dir = app.config.setdefault('FILE_MANAGER_UPLOAD_DIR ', './data/files')
        self._create_upload_dir()

    def retrieve_file_header(self, file: File):
        # Initialize the file header variable
        file_header_str = ""
        # Open the file for reading
        with self.get_file_d(file) as f:
            # Search for the file header start
            for line in f:
                if line.startswith(self.file_header_prefix) and line.endswith(self.file_header_end):
                    file_header_str = line[len(self.file_header_prefix):line.find(self.file_header_end)]

        if file_header_str:
            try:
                file_header = json.loads(file_header_str)
            except json.JSONDecodeError as e:
                current_app.logger.error("The file header can't be loaded. Details: " + str(e))
                raise InvalidFileHeader("The file header can't be loaded. Details: " + str(e))

            self.db_manager.update_file(file, fileInformation=file_header)

    def retrieve_file_info(self, file: File):
        # Open the file for reading
        with self.get_file_d(file) as f:
            # Search for the file header start
            for line in f:
                if line[0] == ";":
                    try:
                        self._identify_file_info(line[1:], file)
                    except (ValueError, TypeError):
                        current_app.logger.error("Can't read the file '" + str(file) + "' information. "
                                                 "Try to obtain it from the header")
                        raise InvalidFileInformation("There was an error retrieving the file information")
                    if file.estimatedPrintingTime is not None and file.estimatedNeededMaterial is not None:
                        break

    def set_job_allowed_config_from_header(self, job: Job):
        # Check that the file header is not empty
        if not job.file.fileInformation:
            current_app.logger.error("Can't read the job allowed config from the file header of the job '" + str(job) +
                                     "'. Details: The file header can't be empty")
            raise InvalidFileHeader("The file header can't be empty")

        try:
            allowed_materials, allowed_extruder_types = self._get_allowed_materials_and_extruder_types(job.file)
        except KeyError as e:
            current_app.logger.error("Can't read the job allowed config from the file header of the job '" + str(job) +
                                     "'. Details: The key " + str(e) + " is missing in the file header")
            raise MissingHeaderKeys("The key " + str(e) + " is missing in the file header")
        except (ValueError, TypeError):
            current_app.logger.error("Can't read the job allowed config from the file header of the job '" + str(job) +
                                     "'. Details: One of the values of the header data is corrupted")
            raise InvalidFileHeader("One of the values of the header data is corrupted")

        # Add the allowed materials and extruder types to the job information
        self.db_manager.insert_job_allowed_materials(job, allowed_materials)
        self.db_manager.insert_job_allowed_extruder_types(job, allowed_extruder_types)

        return job

    def set_file_information_from_header(self, file: File):
        # Check that the file header is not empty
        if not file.fileInformation:
            current_app.logger.error("Can't read the file information from the header of the file'" + str(file) +
                                     "'. Details: The file header can't be empty")
            raise InvalidFileHeader("The file header can't be empty")

        # Get the fields to update of the file
        try:
            fields_to_update = self._get_file_print_information(file)
        except KeyError as e:
            current_app.logger.error("Can't read the file information from the header of the file'" + str(file) +
                                     "'. Details: The key " + str(e) + " is missing in the file header")
            raise MissingHeaderKeys("The key " + str(e) + " is missing in the file header")
        except (ValueError, TypeError):
            current_app.logger.error("Can't read the file information from the header of the file'" + str(file) +
                                     "'. Details: One of the values of the header data is corrupted")
            raise InvalidFileHeader("One of the values of the header data is corrupted")

        # Update the fields in the file object
        self.db_manager.update_file(file, **fields_to_update)

        return file

    def save_file(self, file, user: User, analise_after_save: bool = False):
        # Check that the file is in gcode format
        if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() != 'gcode':
            raise InvalidFileType("The file to save needs to be in gcode format")

        # Generate a random filename that will be used for saving it in the filesystem
        filename = str(uuid.uuid4()) + '.gcode'
        full_path = os.path.join(self.app.config['FILE_MANAGER_UPLOAD_DIR'], secure_filename(filename))

        # Create the file object in the database
        file_obj = self.db_manager.insert_file(user, file.filename, full_path)

        # Save the file to the filesystem
        file.save(full_path)

        # Analise the file (if specified)
        if analise_after_save:
            self.retrieve_file_header(file_obj)

        return file_obj

    def delete_file(self, file: File):
        # Delete the file from the filesystem
        if os.path.exists(file.fullPath):
            os.remove(file.fullPath)
        else:
            raise FilesystemError("File '{}' not found in the filesystem.".format(file.fullPath))

        # Delete the file from the database
        self.db_manager.delete_files(id=file.id)

    @staticmethod
    def get_file_d(file: File):
        # Open the file from the full path
        fd = open(file.fullPath, "r")

        return fd
