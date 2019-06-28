"""
This module defines the file storage manager class
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.0.2"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

import json
import os
import subprocess
import warnings
from datetime import timedelta

import math
from flask import current_app
from werkzeug.utils import secure_filename

from .exceptions import (
    MissingFileDataKeys, InvalidFileType, FilesystemError, InvalidFileData
)
from ..database import DBManager
from ..database import (
    File, Job, User
)


class FileDescriptor(object):
    """
    This class implements a file descriptor object. It will contain the file name, file path (if any), and the flask
    file object (if any)
    """
    def __init__(self, filename, path=None, flask_file_obj=None):
        self.filename = filename
        self.path = path
        self.flask_file = flask_file_obj


class FileManager(object):
    """
    This class implements the interface for save and retrieve files from the filesystem
    """
    def __init__(self, app=None, file_data_prefix=";PrintInfo/",
                 file_data_end="/PrintInfo\n", db_manager: DBManager = None):
        self.app = None
        self.file_data_prefix = file_data_prefix
        self.file_data_end = file_data_end
        self.upload_dir = None

        if app is not None:
            self.init_app(app)

        if db_manager is None:
            from ..database import db_mgr
            self.db_manager = db_mgr
        else:
            self.db_manager = db_manager

    def set_db_manager(self, db_manager):
        self.db_manager = db_manager

    def _create_upload_dir(self):
        os.makedirs(self.app.config.get('FILE_MANAGER_UPLOAD_DIR'), exist_ok=True)

    def _get_allowed_materials_and_extruder_types(self, file: File):
        # Prepare the allowed materials and extruder types data
        allowed_materials = []
        allowed_extruder_types = []

        for i in range(len(list(file.fileData["extruders"]))):
            extruder = dict(file.fileData["extruders"][i])
            if bool(extruder["enabled"]):
                # Get all the materials in the socketio_printer of this type
                materials_of_this_type = \
                    self.db_manager.get_printer_materials(type=str(extruder["material"]["type"]))
                for material in materials_of_this_type:
                    allowed_materials.append((material, i))
                # Get all the extruder types in the socketio_printer of this nozzle diameter
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

        # Get the estimated printing time from the data
        estimated_printing_time = float(file.fileData["print_times"]["total"])
        fields_to_update["estimatedPrintingTime"] = timedelta(seconds=estimated_printing_time)

        # Calculate the estimated needed material for all the extruders
        weight = 0.0
        for extruder in file.fileData["extruders"]:
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

    def _get_extruder_estimated_needed_material(self, file: File):
        # Prepare the extruder estimated needed material array
        extruder_estimated_needed_material = []

        for i in range(len(list(file.fileData["extruders"]))):
            extruder = dict(file.fileData["extruders"][i])
            if bool(extruder["enabled"]):
                # Calculate the weight from the material used in meters and the material data
                material_used_weight = self._calculate_weight_from_filament_distance(
                    extruded_filament_distance=float(extruder["material_used"]),
                    filament_diameter=float(extruder["material"]["diameter"]),
                    filament_density=float(extruder["material"]["density"])
                )
                extruder_estimated_needed_material.append((material_used_weight, i))

        return extruder_estimated_needed_material

    @staticmethod
    def _save_flask_file(flask_file, destination):
        try:
            flask_file.save(destination)
        except OSError:
            raise FilesystemError("Unable to save the file in the server storage")

    @staticmethod
    def _move_file_async(origin, destination):
        try:
            with open(os.devnull, 'w') as fp:
                subprocess.run(["cp", origin, destination], check=True, stdout=fp, stderr=fp)
        except (subprocess.CalledProcessError, OSError) as e:
            raise FilesystemError("Unable to save the file in the server storage")

    def init_app(self, app, create_upload_dir=True):
        self.app = app

        if (
            'FILE_MANAGER_UPLOAD_DIR' not in app.config
        ):
            warnings.warn(
                'FILE_MANAGER_UPLOAD_DIR not set. '
                'Defaulting FILE_MANAGER_UPLOAD_DIR to "./upload_folder/".'
            )

        self.upload_dir = app.config.setdefault('FILE_MANAGER_UPLOAD_DIR ', './data/files')

        if create_upload_dir:
            self._create_upload_dir()

    def retrieve_file_data(self, file: File):
        # Initialize the file data variable
        file_data_str = ""
        # Open the file for reading
        with self.get_file_d(file) as f:
            # Search for the file data start
            for line in f:
                if line.startswith(self.file_data_prefix) and line.endswith(self.file_data_end):
                    file_data_str = line[len(self.file_data_prefix):line.find(self.file_data_end)]

        if file_data_str:
            try:
                file_data = json.loads(file_data_str)
            except json.JSONDecodeError as e:
                current_app.logger.error("The file data can't be loaded. Details: " + str(e))
                raise InvalidFileData("The file data can't be loaded. Details: " + str(e))
            self.db_manager.update_file(file, fileData=file_data)
        else:
            current_app.logger.error(
                "The file data can't be loaded. Details: The file don't contain the data dictionary")
            raise InvalidFileData("The file data can't be loaded. Details: The file don't contain the data dictionary")

    def retrieve_file_basic_info(self, file: File):
        # Open the file for reading
        with self.get_file_d(file) as f:
            # Search for the file data start
            for line in f:
                if line[0] == ";":
                    try:
                        self._identify_file_info(line[1:], file)
                    except (ValueError, TypeError):
                        current_app.logger.error("Can't read the file '" + str(file) + "' information. "
                                                 "Try to obtain it from the file data")
                        raise InvalidFileData("There was an error retrieving the file information")
                    if file.estimatedPrintingTime is not None and file.estimatedNeededMaterial is not None:
                        break

    def set_job_allowed_config_from_file_data(self, job: Job):
        # Check that the file data is not empty
        if not job.file.fileData:
            current_app.logger.error("Can't read the allowed config from the file data of the job '" + str(job) +
                                     "'. Details: The file data can't be empty")
            raise InvalidFileData("The file data can't be empty")

        try:
            allowed_materials, allowed_extruder_types = self._get_allowed_materials_and_extruder_types(job.file)
        except KeyError as e:
            current_app.logger.error("Can't read the allowed config from the file data of the job '" + str(job) +
                                     "'. Details: The key " + str(e) + " is missing in the file data")
            raise MissingFileDataKeys("The key " + str(e) + " is missing in the file data")
        except (ValueError, TypeError):
            current_app.logger.error("Can't read the allowed config from the file data of the job '" + str(job) +
                                     "'. Details: One of the values of the file data is corrupted")
            raise InvalidFileData("One of the values of the file data is corrupted")

        # Add the allowed materials and extruder types to the job information
        self.db_manager.insert_job_allowed_materials(job, allowed_materials)
        self.db_manager.insert_job_allowed_extruder_types(job, allowed_extruder_types)

        # Set the job 'analyzed' flag to true
        self.db_manager.update_job(job, analyzed=True)

        return job

    def set_file_information_from_file_data(self, file: File):
        # Check that the file data is not empty
        if not file.fileData:
            current_app.logger.error("Can't read the file information from the data of the file '" + str(file) +
                                     "'. Details: The file data can't be empty")
            raise InvalidFileData("The file data can't be empty")

        # Get the fields to update of the file
        try:
            fields_to_update = self._get_file_print_information(file)
        except KeyError as e:
            current_app.logger.error("Can't read the file information from the data of the file '" + str(file) +
                                     "'. Details: The key " + str(e) + " is missing in the file data")
            raise MissingFileDataKeys("The key " + str(e) + " is missing in the file data")
        except (ValueError, TypeError):
            current_app.logger.error("Can't read the file information from the data of the file '" + str(file) +
                                     "'. Details: One of the values of the file data is corrupted")
            raise InvalidFileData("One of the values of the file data is corrupted")

        # Update the fields in the file object
        self.db_manager.update_file(file, **fields_to_update)

        return file

    def set_job_estimated_needed_material_from_file_data(self, job: Job):
        # Check that the file data is not empty
        if not job.file.fileData:
            current_app.logger.error("Can't read the estimated needed material from the file data of the job '"
                                     + str(job) + "'. Details: The file data can't be empty")
            raise InvalidFileData("The file data can't be empty")
        
        # Get the fields to update of the file
        try:
            extruders_estimated_needed_materials = self._get_extruder_estimated_needed_material(job.file)
        except KeyError as e:
            current_app.logger.error("Can't read the estimated needed material from the file data of the job '"
                                     + str(job) + "'. Details: The key " + str(e) + " is missing in the file data")
            raise MissingFileDataKeys("The key " + str(e) + " is missing in the file data")
        except (ValueError, TypeError):
            current_app.logger.error("Can't read the estimated needed material from the file data of the job '"
                                     + str(job) + "'. Details: One of the values of the file data is corrupted")
            raise InvalidFileData("One of the values of the file data is corrupted")
        
        # Update the job extruders data
        for estimated_needed_material, index in extruders_estimated_needed_materials:
            # Get the job extruder data for this extruder index
            job_extruder = self.db_manager.get_job_extruders(job, extruder_index=index)

            # Check if the job extruder data already exist for this extruder index, if not create it
            if not job_extruder:
                job_extruder = self.db_manager.insert_job_extruders(job, [index])[0]
            else:
                job_extruder = job_extruder[0]

            # Update the job estimated needed material
            self.db_manager.update_job_extruder(job_extruder, estimatedNeededMaterial=estimated_needed_material)

        return job

    def save_file(self, file: FileDescriptor, user: User):
        # Check that the file is in gcode format
        if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() != 'gcode':
            raise InvalidFileType("The file to save needs to be in gcode format")

        # Create the file object in the socketio_printer
        file_obj = self.db_manager.insert_file(user, file.filename)

        # Set the file ID as the new filename and generate the destination path
        filename = str(file_obj.id)
        destination_path = os.path.join(self.app.config['FILE_MANAGER_UPLOAD_DIR'], secure_filename(filename))

        # Save the file to the filesystem
        try:
            if file.flask_file is not None:
                self._save_flask_file(file.flask_file, destination_path)
            else:
                self._move_file_async(file.path, destination_path)
        except FilesystemError as e:
            self.db_manager.delete_file(file_obj)
            raise e

        # Update the file path
        self.db_manager.update_file(file_obj, fullPath=destination_path)

        return file_obj

    def delete_file(self, file: File):
        # Delete the file from the filesystem
        if os.path.exists(file.fullPath):
            os.remove(file.fullPath)
        else:
            raise FilesystemError("File '{}' not found in the filesystem.".format(file.fullPath))

        # Delete the file from the socketio_printer
        self.db_manager.delete_file(file)

    @staticmethod
    def get_file_d(file: File):
        # Open the file from the full path
        if os.path.exists(file.fullPath):
            try:
                fd = open(file.fullPath, "r")
                return fd
            except (OSError, IOError):
                raise FilesystemError("Can't retrieve the file from filesystem.".format(file.fullPath))
        else:
            raise FilesystemError("File '{}' not found in the filesystem.".format(file.fullPath))
