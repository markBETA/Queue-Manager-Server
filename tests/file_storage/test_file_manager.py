from shutil import copyfile
import os
import time


def test_file_manager_class(file_manager):
    class FlaskFile(object):
        def __init__(self, filename, full_path):
            self.filename = filename
            self.origin_full_path = full_path

        def save(self, destination_path):
            copyfile(self.origin_full_path, destination_path)

    db_manager = file_manager.db_manager

    user = db_manager.get_users(id=1)
    file = FlaskFile("test-file.gcode", "./test-file.gcode")

    file_obj = file_manager.save_file(file, user, analise_after_save=False)
    assert file_obj.name == file.filename
    assert file_obj.user == user
    assert os.path.isfile(file_obj.fullPath)

    initial_time = time.time()

    file_manager.retrieve_file_header(file_obj)

    print("Total time for retrieve the header:", time.time() - initial_time)

    job = db_manager.insert_job("test-job", file_obj, user)

    file_manager.set_job_allowed_config_from_header(job)

    assert len(job.allowed_materials) == 1
    assert len(job.allowed_extruder_types) == 1

    assert job.allowed_materials[0].material.type == "PLA"
    assert job.allowed_extruder_types[0].type.nozzleDiameter == 0.6

    file_manager.set_file_information_from_header(file_obj)

    assert file_obj.estimatedPrintingTime.total_seconds() == 7070.0
    assert round(file_obj.estimatedNeededMaterial) == 11

    db_manager.update_file(file_obj, estimatedPrintingTime=None, estimatedNeededMaterial=None)

    initial_time = time.time()

    file_manager.retrieve_file_info(file_obj)

    print("Total time for retrieve the info:", time.time() - initial_time)

    assert file_obj.estimatedPrintingTime.total_seconds() == 7069.0
    assert round(file_obj.estimatedNeededMaterial) == 11

    file_manager.delete_file(file_obj)

    assert not os.path.isfile(file_obj.fullPath)
