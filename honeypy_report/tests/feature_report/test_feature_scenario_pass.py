import pytest

from copy import deepcopy

from honeypy_report.tests.assertions import Assertions
from honeypy.api.report import ReportService
from honeypy.api.test import TestService

from bson.objectid import ObjectId

test_service = TestService()
report_service = ReportService()
assertions = Assertions()

def pytest_namespace():
    return {
        'report_id': None,
        'feature': {}
    }

feature = {
    "path":"feature_report.feature",
    "kind":"feature",
    "host":"Localhost"
}

report_save = deepcopy(feature)
report_save["browser"] = "firefox"
report_save["fail"] = True
report_save["host"] = "Other Host"

scenario_id_1 = str(ObjectId())
scenario_id_2 = str(ObjectId())

scenario_1 = {
    "type":"scenario",
    "text":"Scenario: Test Things",
    "name":"Test Things",
    "scenarioId": scenario_id_1,
    "tests":[],
    "result": True,
    "message": "Success"
}

scenario_1_tests = [
    {
        "kind":"feature",
        "type":"step",
        "test":"Given I do things",
        "text":"Given I do things",
        "result": True,
        "message": "Success",
        "scenarioId": scenario_id_1
    },
    {
        "kind":"feature",
        "type":"step",
        "test":"When I do things",
        "text":"When I do things",
        "result": True,
        "message": "Pass The Things",
        "scenarioId": scenario_id_1
    },
    {
        "kind":"feature",
        "type":"step",
        "test":"Then I do things",
        "text":"Then I do things",
        "result": True,
        "message": "Success",
        "scenarioId": scenario_id_1
    }
]

scenario_2 = {
    "kind":"feature",
    "type":"scenario",
    "text":"Scenario: 2 Test Things",
    "name":"2 Test Things",
    "scenarioId": scenario_id_2,
    "tests":[],
    "result": True,
    "message": "PASSING"
}

scenario_2_tests = [
    {
        "kind":"feature",
        "type":"step",
        "test":"Given I do things again",
        "text":"Given I do things again",
        "result": True,
        "message": "Success",
        "scenarioId": scenario_id_2
    },
    {
        "kind":"feature",
        "type":"step",
        "test":"When I do things again",
        "text":"When I do things again",
        "result": True,
        "message": "Pass The Things",
        "scenarioId": scenario_id_2
    },
    {
        "kind":"feature",
        "type":"step",
        "test":"Then I do things again",
        "text":"Then I do things again",
        "result": True,
        "message": "Success",
        "scenarioId": scenario_id_2
    }
]

def test_setup_data():
    test_service.delete(feature["path"], "feature")
    response = test_service.create(feature)
    assert response.status_code == 201
    response = test_service.get(feature["path"], "feature")
    assert response.status_code == 200
    pytest.feature = response.json()

def test_create_report():
    response = report_service.create(pytest.feature)
    assert response.status_code == 201
    data = response.json()
    pytest.report_id = data["id"]
    assert len(data["id"]) == 24

def test_start_report():
    response = report_service.save(pytest.report_id, {"kind": "feature", "status": "Running"})
    assert response.status_code == 204

def test_verify_report_created():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()

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
    assert data["status"] == "Running"
    assert data["fail"] == report_save["fail"]
    assert data["kind"] == feature["kind"]
    assert data["path"] == feature["path"]
    assert data["contents"] == []

#
# Add a single scenario with subtests
#

def test_add_scenario_1():
    response = report_service.add(pytest.report_id, scenario_1)
    assert response.status_code == 204

def test_verify_added_scenario_1():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Running"
    assert len(data["tests"]) == 1
    assert data["tests"][0]["type"] == scenario_1["type"]
    assert data["tests"][0]["text"] == scenario_1["text"]
    assert data["tests"][0]["name"] == scenario_1["name"]
    assert data["tests"][0]["tests"] == scenario_1["tests"]
    assert data["tests"][0]["result"] == scenario_1["result"]
    assert data["tests"][0]["message"] == scenario_1["message"]
    assert data["tests"][0]["created"]

def test_add_scenario_1_test_1():
    response = report_service.add(pytest.report_id, scenario_1_tests[0])
    assert response.status_code == 204

def test_verify_added_scenario_1_test_1():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Running"
    assert len(data["tests"]) == 1
    assert len(data["tests"][0]["tests"]) == 1
    assert data["tests"][0]["result"] == scenario_1["result"]
    assert data["tests"][0]["message"] == scenario_1["message"]
    assert data["tests"][0]["tests"][0]["type"] == scenario_1_tests[0]["type"]
    assert data["tests"][0]["tests"][0]["result"] == scenario_1_tests[0]["result"]
    assert data["tests"][0]["tests"][0]["message"] == scenario_1_tests[0]["message"]
    assert data["tests"][0]["tests"][0]["scenarioId"] == scenario_1_tests[0]["scenarioId"]
    assert data["tests"][0]["tests"][0]["test"] == scenario_1_tests[0]["test"]
    assert data["tests"][0]["tests"][0]["text"] == scenario_1_tests[0]["text"]

def test_add_scenario_1_test_2():
    response = report_service.add(pytest.report_id, scenario_1_tests[1])
    assert response.status_code == 204

def test_verify_added_scenario_1_test_2():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Running"
    assert len(data["tests"]) == 1
    assert len(data["tests"][0]["tests"]) == 2
    assert data["tests"][0]["result"] == scenario_1["result"]
    assert data["tests"][0]["message"] == scenario_1["message"]
    assert data["tests"][0]["tests"][1]["type"] == scenario_1_tests[1]["type"]
    assert data["tests"][0]["tests"][1]["result"] == scenario_1_tests[1]["result"]
    assert data["tests"][0]["tests"][1]["message"] == scenario_1_tests[1]["message"]
    assert data["tests"][0]["tests"][1]["scenarioId"] == scenario_1_tests[1]["scenarioId"]
    assert data["tests"][0]["tests"][1]["test"] == scenario_1_tests[1]["test"]
    assert data["tests"][0]["tests"][1]["text"] == scenario_1_tests[1]["text"]

def test_add_scenario_1_test_3():
    response = report_service.add(pytest.report_id, scenario_1_tests[2])
    assert response.status_code == 204

def test_verify_added_scenario_1_test_3():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Running"
    assert len(data["tests"]) == 1
    assert len(data["tests"][0]["tests"]) == 3
    assert data["tests"][0]["result"] == scenario_1["result"]
    assert data["tests"][0]["message"] == scenario_1["message"]
    assert data["tests"][0]["tests"][2]["type"] == scenario_1_tests[2]["type"]
    assert data["tests"][0]["tests"][2]["result"] == scenario_1_tests[2]["result"]
    assert data["tests"][0]["tests"][2]["message"] == scenario_1_tests[2]["message"]
    assert data["tests"][0]["tests"][2]["scenarioId"] == scenario_1_tests[2]["scenarioId"]
    assert data["tests"][0]["tests"][2]["test"] == scenario_1_tests[2]["test"]
    assert data["tests"][0]["tests"][2]["text"] == scenario_1_tests[2]["text"]

#
# Add a single scenario with subtests
#

def test_add_scenario_2():
    response = report_service.add(pytest.report_id, scenario_2)
    assert response.status_code == 204

def test_verify_added_scenario_2():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Running"
    assert len(data["tests"]) == 2
    assert data["tests"][1]["type"] == scenario_2["type"]
    assert data["tests"][1]["text"] == scenario_2["text"]
    assert data["tests"][1]["name"] == scenario_2["name"]
    assert data["tests"][1]["tests"] == scenario_2["tests"]
    assert data["tests"][1]["result"] == scenario_2["result"]
    assert data["tests"][1]["message"] == scenario_2["message"]
    assert data["tests"][1]["created"]

def test_add_scenario_2_test_1():
    response = report_service.add(pytest.report_id, scenario_2_tests[0])
    assert response.status_code == 204

def test_verify_added_scenario_2_test_1():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Running"
    assert len(data["tests"]) == 2
    assert len(data["tests"][1]["tests"]) == 1
    assert data["tests"][1]["result"] == scenario_2["result"]
    assert data["tests"][1]["message"] == scenario_2["message"]
    assert data["tests"][1]["tests"][0]["type"] == scenario_2_tests[0]["type"]
    assert data["tests"][1]["tests"][0]["result"] == scenario_2_tests[0]["result"]
    assert data["tests"][1]["tests"][0]["message"] == scenario_2_tests[0]["message"]
    assert data["tests"][1]["tests"][0]["scenarioId"] == scenario_2_tests[0]["scenarioId"]
    assert data["tests"][1]["tests"][0]["test"] == scenario_2_tests[0]["test"]
    assert data["tests"][1]["tests"][0]["text"] == scenario_2_tests[0]["text"]

def test_add_scenario_2_test_2():
    response = report_service.add(pytest.report_id, scenario_2_tests[1])
    assert response.status_code == 204

def test_verify_added_scenario_2_test_2():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Running"
    assert len(data["tests"]) == 2
    assert len(data["tests"][1]["tests"]) == 2
    assert data["tests"][1]["result"] == scenario_2["result"]
    assert data["tests"][1]["message"] == scenario_2["message"]
    assert data["tests"][1]["tests"][1]["type"] == scenario_2_tests[1]["type"]
    assert data["tests"][1]["tests"][1]["result"] == scenario_2_tests[1]["result"]
    assert data["tests"][1]["tests"][1]["message"] == scenario_2_tests[1]["message"]
    assert data["tests"][1]["tests"][1]["scenarioId"] == scenario_2_tests[1]["scenarioId"]
    assert data["tests"][1]["tests"][1]["test"] == scenario_2_tests[1]["test"]
    assert data["tests"][1]["tests"][1]["text"] == scenario_2_tests[1]["text"]

def test_add_scenario_2_test_3():
    response = report_service.add(pytest.report_id, scenario_2_tests[2])
    assert response.status_code == 204

def test_verify_added_scenario_2_test_3():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Running"
    assert len(data["tests"]) == 2
    assert len(data["tests"][1]["tests"]) == 3
    assert data["tests"][1]["result"] == scenario_2["result"]
    assert data["tests"][1]["message"] == scenario_2["message"]
    assert data["tests"][1]["tests"][2]["type"] == scenario_2_tests[2]["type"]
    assert data["tests"][1]["tests"][2]["result"] == scenario_2_tests[2]["result"]
    assert data["tests"][1]["tests"][2]["message"] == scenario_2_tests[2]["message"]
    assert data["tests"][1]["tests"][2]["scenarioId"] == scenario_2_tests[2]["scenarioId"]
    assert data["tests"][1]["tests"][2]["test"] == scenario_2_tests[2]["test"]
    assert data["tests"][1]["tests"][2]["text"] == scenario_2_tests[2]["text"]

def test_finish_feature():
    response = report_service.finish(pytest.report_id)
    assert response.status_code == 204

def test_verify_finish():
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    data = response.json()
    assert len(data["tests"]) == 2
    assert len(data["tests"][0]["tests"]) == 3
    assert len(data["tests"][1]["tests"]) == 3
    assert data["tests"][0]["result"] == scenario_1["result"]
    assert data["tests"][0]["message"] == scenario_1["message"]
    assert data["tests"][1]["result"] == scenario_2["result"]
    assert data["tests"][1]["message"] == scenario_2["message"]
    assert data["message"] == "Success"
    assert data["status"] == "Done"
    assert data["result"] == True
    assert data["end"]
