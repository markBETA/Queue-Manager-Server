import json
from datetime import timedelta

from flask_restplus import marshal

from queuemanager.api.files import file_model


def test_file_model(db_manager):
        user = db_manager.get_users(username="bcn3d")
        file = db_manager.insert_file(user, "test-file", "./test-file",
                                      estimatedPrintingTime=timedelta(hours=3, minutes=12, seconds=10.2),
                                      estimatedNeededMaterial=105.2)
        print(json.dumps(marshal(file, file_model)))
