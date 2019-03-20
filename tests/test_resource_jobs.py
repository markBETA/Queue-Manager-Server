import io
import os
from tests.globals import GCODES
from queuemanager.models.User import User
from queuemanager.models.Job import Job
from queuemanager.models.Queue import Queue


def test_get_jobs(client, app):
    with app.app_context():
        res = client.get("/queuemanagerapi/jobs")
        assert res.status_code == 200
        assert len(res.json) == len(GCODES)
        for i in range(0, len(res.json)):
            job = res.json[i]
            user = job.get("user")
            assert user.get("username") == "eloi"
            assert job.get("order") == i + 1
            assert job.get("name") == GCODES[i].get("job_name")
            assert job.get("file").get("time") == GCODES[i].get("time")
            assert job.get("file").get("used_material") == GCODES[i].get("filament")
            assert job.get("file").get("name") == GCODES[i].get("file_name")
            assert os.path.exists(Job.query.get(job.get("id")).file.path)
            for extruder in job.get("file").get("used_extruders"):
                assert float(GCODES[i].get("extruders").get(str(extruder.get("index")))) == extruder.get("nozzle_diameter")


def test_get_job(client, app):
    with app.app_context():
        res = client.get("/queuemanagerapi/jobs/1")
        assert res.status_code == 200
        assert res.json.get("name") == GCODES[0].get("job_name")
        user = res.json.get("user")
        assert user.get("username") == "eloi"
        assert res.json.get("order") == 1
        assert res.json.get("name") == GCODES[0].get("job_name")
        assert res.json.get("file").get("time") == GCODES[0].get("time")
        assert res.json.get("file").get("used_material") == GCODES[0].get("filament")
        assert res.json.get("file").get("name") == GCODES[0].get("file_name")
        assert os.path.exists(Job.query.get(res.json.get("id")).file.path)
        for extruder in res.json.get("file").get("used_extruders"):
            assert float(GCODES[0].get("extruders").get(str(extruder.get("index")))) == extruder.get("nozzle_diameter")


def test_post_nonauth_job(client, app):
    with app.app_context():
        filepath = os.path.join(app.config.get("TEST_INPUTS_PATH"), "S_Cono.gcode")
        file = io.FileIO(filepath)
        body = {"name": "cono", "gcode": file}
        res = client.post("/queuemanagerapi/jobs", data=body)
        assert res.status_code == 401
        assert res.json.get("message") == "Missing Authorization header"


def test_post_existing_job(client, app):
    with app.app_context():
        user = User.query.filter_by(username="eloi").first()
        token = User.encode_auth_token(user.id)
        filepath = os.path.join(app.config.get("TEST_INPUTS_PATH"), "S_BMO.gcode")
        file = io.FileIO(filepath)
        body = {"name": "bmo", "gcode": file}
        res = client.post("/queuemanagerapi/jobs", data=body, headers={"Authorization": token.decode()})
        assert res.status_code == 409
        assert res.json.get("message") == "File path already exists"


def test_post_job(client, app):
    NEW_JOB = {
        "job_name": "cono",
        "file_name": "S_Cono.gcode",
        "time": 147,
        "filament": 0.0593156,
        "extruders": {
            0: 0.6
        }
    }
    with app.app_context():
        user = User.query.filter_by(username="eloi").first()
        token = User.encode_auth_token(user.id)
        filepath = os.path.join(app.config.get("TEST_INPUTS_PATH"), "S_Cono.gcode")
        file = io.FileIO(filepath)
        body = {"name": NEW_JOB.get("job_name"), "gcode": file}
        res = client.post("/queuemanagerapi/jobs", data=body, headers={"Authorization": token.decode()})
        assert res.status_code == 201
        assert res.json.get("name") == NEW_JOB.get("job_name")
        assert res.json.get("order") == 5
        assert res.json.get("file").get("name") == NEW_JOB.get("file_name")
        assert res.json.get("file").get("time") == NEW_JOB.get("time")
        assert res.json.get("file").get("used_material") == NEW_JOB.get("filament")
        assert os.path.exists(Job.query.get(res.json.get("id")).file.path)
        for extruder in res.json.get("file").get("used_extruders"):
            assert extruder.get("nozzle_diameter") == NEW_JOB.get("extruders").get(extruder.get("index"))


def test_delete_job(client, app):
    with app.app_context():
        user = User.query.filter_by(username="eloi").first()
        token = User.encode_auth_token(user.id)
        jobs_before_delete = Job.query.all()
        res = client.delete("/queuemanagerapi/jobs/1", headers={"Authorization": token.decode()})
        jobs_after_delete = Job.query.all()
        assert res.json.get("id") == 1
        assert len(jobs_before_delete) == len(jobs_after_delete) + 1
        assert res.json not in jobs_after_delete


def test_update_job(client, app):
    with app.app_context():
        user = User.query.filter_by(username="admin").first()
        token = User.encode_auth_token(user.id)
        body = {"name": "test", "order": 1}
        res = client.put("/queuemanagerapi/jobs/3", data=body, headers={"Authorization": token.decode()})
        assert res.json.get("name") == "test"
        assert res.json.get("order") == 1
        assert res.json.get("updated_at") is not None

        queues = Queue.query.all()
        for queue in queues:
            for i in range(0, len(queue.jobs)):
                assert queue.jobs[i].order == i + 1
