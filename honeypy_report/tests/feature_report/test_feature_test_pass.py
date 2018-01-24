import pytest
from copy import deepcopy
from honeypy.api.report import ReportService
from honeypy.api.test import TestService
from bson.objectid import ObjectId

test_service = TestService()
report_service = ReportService()

def pytest_namespace():
    return {
        'report_id': None
    }

feature = {
    "path":"feature_report.feature",
    "kind":"feature"
}

report = {
    "kind":"feature",
    "path":feature["path"]
}

report_save = deepcopy(report)
report_save["browser"] = "firefox"
report_save["host"] = "host_test"

tests = [
    {
        "kind":"feature",
        "_type":"test",
        "test":"Given I do things",
        "text":"Given I do things",
        "result": True,
        "message": "Success"
    },
    {
        "kind":"feature",
        "_type":"test",
        "test":"Given I do other things",
        "text":"Given I do other things",
        "result": True,
        "message": "Test Success"
    },
    {
        "kind":"feature",
        "_type":"test",
        "test":"When I stop things",
        "text":"When I stop things",
        "result": True,
        "message": "Success"
    }
]

def test_setup_feature():
    test_service.delete(feature["path"], "feature")
    response = test_service.create(feature)
    assert response.status_code == 201

def test_create_report():
    response = report_service.create(report)
    assert response.status_code == 201
    data = response.json()
    pytest.report_id = data["id"]
    assert data["id"]

def test_verify_report_created():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert data["_id"]
    assert data["tests"] == []
    assert data["created"]
    assert data["modified"]
    assert data["host"] == "Localhost"
    assert data["url"] == ""
    assert data["browser"] == "chrome"
    assert data["message"] == "Incomplete"
    assert data["fail"] == False
    assert data["errors"] == []
    assert data["kind"] == report["kind"]
    assert data["path"] == report["path"]
    assert data["content"] == []

def test_verify_report_save():
    response = report_service.save(pytest.report_id, report_save)
    assert response.status_code == 204

def test_verify_save_persists():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert data["_id"]
    assert data["tests"] == []
    assert data["created"]
    assert data["modified"]
    assert data["created"] != data["modified"]
    assert data["host"] == report_save["host"]
    assert data["url"] == ""
    assert data["browser"] == report_save["browser"]
    assert data["message"] == "Incomplete"
    assert data["fail"] == False
    assert data["errors"] == []
    assert data["kind"] == report["kind"]
    assert data["path"] == report["path"]
    assert data["content"] == []

def test_add_test_1():
    response = report_service.add(pytest.report_id, tests[0])
    assert response.status_code == 204

def test_verify_added_test_1():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert len(data["tests"]) == 1
    assert data["message"] == "Incomplete"
    assert data["tests"][0]["_type"] == tests[0]["_type"]
    assert data["tests"][0]["text"] == tests[0]["text"]
    assert data["tests"][0]["test"] == tests[0]["test"]
    assert data["tests"][0]["result"] == tests[0]["result"]
    assert data["tests"][0]["created"]

def test_add_test_2():
    response = report_service.add(pytest.report_id, tests[1])
    assert response.status_code == 204

def test_verify_added_test_2():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert len(data["tests"]) == 2
    assert data["message"] == "Incomplete"
    assert data["tests"][1]["_type"] == tests[1]["_type"]
    assert data["tests"][1]["text"] == tests[1]["text"]
    assert data["tests"][1]["test"] == tests[1]["test"]
    assert data["tests"][1]["result"] == tests[1]["result"]
    assert data["tests"][1]["created"]

def test_add_test_3():
    response = report_service.add(pytest.report_id, tests[2])
    assert response.status_code == 204

def test_verify_added_test_3():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert len(data["tests"]) == 3
    assert data["message"] == "Incomplete"
    assert data["tests"][2]["_type"] == tests[2]["_type"]
    assert data["tests"][2]["text"] == tests[2]["text"]
    assert data["tests"][2]["test"] == tests[2]["test"]
    assert data["tests"][2]["result"] == tests[2]["result"]
    assert data["tests"][2]["created"]

def test_finish_feature():
    response = report_service.finish(pytest.report_id)
    assert response.status_code == 204

def test_verify_finish():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert len(data["tests"]) == 3
    assert data["message"] == "Success"
    assert data["result"] == True
    assert data["end"]
