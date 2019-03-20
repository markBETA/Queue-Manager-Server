def test_get_queues(client):
    res = client.get("/queuemanagerapi/queues")
    assert len(res.json) == 2


def test_get_active_queue(client):
    res = client.get("/queuemanagerapi/queues/active")
    assert res.json.get("active")


def test_get_waiting_queue(client):
    res = client.get("/queuemanagerapi/queues/waiting")
    assert not res.json.get("active")
