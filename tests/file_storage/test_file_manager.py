import os
import time
from shutil import copyfile


def test_file_manager_class(db_manager, file_manager):
    class FlaskFile(object):
        def __init__(self, filename, full_path):
            self.filename = filename
            self.origin_full_path = full_path

        def save(self, destination_path):
            copyfile(self.origin_full_path, destination_path)

    user = db_manager.get_users(id=1)
    file = FlaskFile("test-file.gcode", "./test-file.gcode")

    file_obj = file_manager.save_file(file, user, analise_after_save=False)
    assert file_obj.name == file.filename
    assert file_obj.user == user
    assert os.path.isfile(file_obj.fullPath)

    initial_time = time.time()

    file_manager.retrieve_file_data(file_obj)

    print("Total time for retrieve the data:", time.time() - initial_time)

    job = db_manager.insert_job("test-job", file_obj, user)

    assert job.analyzed is False

    file_manager.set_job_allowed_config_from_file_data(job)

    assert len(job.allowed_materials) == 1
    assert len(job.allowed_extruder_types) == 1
    assert job.analyzed is True

    assert job.allowed_materials[0].material.type == "PLA"
    assert job.allowed_materials[0].extruderIndex == 0
    assert job.allowed_extruder_types[0].type.nozzleDiameter == 0.6
    assert job.allowed_extruder_types[0].extruderIndex == 0

    file_manager.set_file_information_from_file_data(file_obj)

    assert file_obj.estimatedPrintingTime.total_seconds() == 101.0
    assert round(file_obj.estimatedNeededMaterial, 2) == 0.32

    file_manager.set_job_estimated_needed_material_from_file_data(job)

    assert len(job.extruders_data) == 1
    assert round(job.extruders_data[0].estimatedNeededMaterial, 2) == 0.32
    assert job.extruders_data[0].extruderIndex == 0

    db_manager.update_file(file_obj, estimatedPrintingTime=None, estimatedNeededMaterial=None)

    initial_time = time.time()

    file_manager.retrieve_file_basic_info(file_obj)

    print("Total time for retrieve the info:", time.time() - initial_time)

    assert file_obj.estimatedPrintingTime.total_seconds() == 100.0
    assert round(file_obj.estimatedNeededMaterial, 2) == 0.28

    file_manager.delete_file(file_obj)

    assert not os.path.isfile(file_obj.fullPath)
