import pytest
from copy import deepcopy
from honeypy.api.report import ReportService
from honeypy.api.test import TestService
from honeypy.api.set import SetService
from bson.objectid import ObjectId

# Initiate services
test_service = TestService()
set_service = SetService()
report_service = ReportService()

def pytest_namespace():
    return {
        'report_id': None
    }

# define test feature a
feature_a = {
    "path":"feature_report_a.feature",
    "kind":"feature"
}

# define test feature b
feature_b = {
    "path":"feature_report_b.feature",
    "kind":"feature"
}

# define test feature c
feature_c = {
    "path":"feature_report_c.feature",
    "kind":"feature"
}

# define the set
# the set should contain the features above
# the set will be used as the payload to create the set report
_set = {
    "kind": "set",
    "name": "Test Set",
    "features": [
        feature_a["path"],
        feature_b["path"],
        feature_c["path"]
    ]
}

# Define scenario ID variables
scenario_id_a = str(ObjectId())
scenario_id_b = str(ObjectId())

# Define a scenario
scenario_a = {
    "kind":"set",
    "_type":"scenario",
    "text":"Scenario: Test Things",
    "name":"Test Things",
    "scenarioId": scenario_id_a,
    "tests":[],
    "result": True,
    "message": "Success"
}

# Define scenario tests
scenario_a_tests = [
    {
        "kind":"set",
        "_type":"test",
        "test":"Given I do things",
        "text":"Given I do things",
        "result": True,
        "message": "Success",
        "scenarioId": scenario_id_a
    },
    {
        "kind":"set",
        "_type":"test",
        "test":"When I do things",
        "text":"When I do things",
        "result": False,
        "message": "Fail the things",
        "scenarioId": scenario_id_a
    },
    {
        "kind":"set",
        "_type":"test",
        "test":"Then I do things",
        "text":"Then I do things",
        "result": True,
        "message": "Success",
        "scenarioId": scenario_id_a
    }
]

# Define a scenario
scenario_b = {
    "kind":"set",
    "_type":"scenario",
    "text":"Scenario: 2 Test Things",
    "name":"2 Test Things",
    "scenarioId": scenario_id_b,
    "tests":[],
    "result": True,
    "message": "PASSING"
}

# Define scenario tests
scenario_b_tests = [
    {
        "kind":"set",
        "_type":"test",
        "test":"Given I do things again",
        "text":"Given I do things again",
        "result": True,
        "message": "Success",
        "scenarioId": scenario_id_b
    },
    {
        "kind":"set",
        "_type":"test",
        "test":"When I do things again",
        "text":"When I do things again",
        "result": True,
        "message": "Pass The Things",
        "scenarioId": scenario_id_b
    },
    {
        "kind":"set",
        "_type":"test",
        "test":"Then I do things again",
        "text":"Then I do things again",
        "result": True,
        "message": "Success",
        "scenarioId": scenario_id_b
    }
]

def test_create_features():
    """
        Setup test data
        Delete and recreate the features
    """
    test_service.delete(feature_a["path"], "feature")
    response = test_service.create(feature_a)
    assert response.status_code == 201

    test_service.delete(feature_b["path"], "feature")
    response = test_service.create(feature_b)
    assert response.status_code == 201

    test_service.delete(feature_c["path"], "feature")
    response = test_service.create(feature_c)
    assert response.status_code == 201

def test_create_set():
    """
        Create a test set
    """
    set_service.delete(_set["name"])
    response = set_service.create(_set)
    assert response.status_code == 201

def test_get_set():
    """
        Get the set by name
    """
    response = set_service.get(_set["name"])
    assert response.status_code == 200
    assert response.json()["name"] == _set["name"]
    assert response.json()["features"] == _set["features"]
    pytest._set = response.json()

def test_create_report():
    """
        Create the report with the set
    """
    response = report_service.create(pytest._set)
    assert response.status_code == 201
    assert response.json()["id"]
    pytest.report_id = response.json()["id"]

def test_get_report():
    """
        Get the report by ID
    """
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

def test_verify_incomplete_set_report():
    """
        Verify the set report is correct
    """
    assert not "status" in pytest.report
    assert pytest.report["message"] == "Incomplete"
    assert pytest.report["features"] == pytest._set["features"]
    assert pytest.report["kind"] == pytest._set["kind"]
    assert pytest.report["name"] == pytest._set["name"]
    assert len(pytest.report["tests"]) == 3
    assert pytest.report["tests"][0]["path"] == pytest._set["features"][0]
    assert pytest.report["tests"][0]["result"] == None
    assert pytest.report["tests"][0]["message"] == "Incomplete"
    assert pytest.report["tests"][1]["path"] == pytest._set["features"][1]
    assert pytest.report["tests"][1]["result"] == None
    assert pytest.report["tests"][1]["message"] == "Incomplete"
    assert pytest.report["tests"][2]["path"] == pytest._set["features"][2]
    assert pytest.report["tests"][2]["result"] == None
    assert pytest.report["tests"][2]["message"] == "Incomplete"

def test_add_scenario_a_feature_a():
    """
        Add scenario A to feature A
        Verify it was added
    """
    scenario_a["path"] = feature_a["path"]
    response = report_service.add(pytest.report_id, scenario_a)
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["message"] == "Incomplete"
    assert len(pytest.report["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][1]["tests"]) == 0
    assert len(pytest.report["tests"][2]["tests"]) == 0

    assert pytest.report["tests"][0]["tests"][0]["_type"] == scenario_a["_type"]
    assert pytest.report["tests"][0]["tests"][0]["name"] == scenario_a["name"]
    assert pytest.report["tests"][0]["tests"][0]["text"] == scenario_a["text"]
    assert pytest.report["tests"][0]["tests"][0]["message"] == "Success"
    assert pytest.report["tests"][0]["tests"][0]["result"] == True
    assert pytest.report["tests"][0]["tests"][0]["tests"] == []

def test_add_subtest_1_scenario_a_feature_a():
    """
        Add a test to scenario a within feature A
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_a_tests[0]["path"] = feature_a["path"]
    response = report_service.add(pytest.report_id, scenario_a_tests[0])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["message"] == "Incomplete"
    assert len(pytest.report["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][1]["tests"]) == 0
    assert len(pytest.report["tests"][2]["tests"]) == 0
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1

    assert pytest.report["tests"][0]["tests"][0]["tests"][0]["path"] == scenario_a_tests[0]["path"]
    assert pytest.report["tests"][0]["tests"][0]["tests"][0]["test"] == scenario_a_tests[0]["test"]
    assert pytest.report["tests"][0]["tests"][0]["tests"][0]["text"] == scenario_a_tests[0]["text"]
    assert pytest.report["tests"][0]["tests"][0]["tests"][0]["result"] == scenario_a_tests[0]["result"]
    assert pytest.report["tests"][0]["tests"][0]["tests"][0]["message"] == scenario_a_tests[0]["message"]

def test_add_scenario_b_feature_a():
    """
        Add scenario B to feature A
    """
    scenario_b["path"] = feature_a["path"]
    response = report_service.add(pytest.report_id, scenario_b)
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["message"] == "Incomplete"
    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 0
    assert len(pytest.report["tests"][2]["tests"]) == 0
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 0

    assert pytest.report["tests"][0]["tests"][1]["_type"] == scenario_b["_type"]
    assert pytest.report["tests"][0]["tests"][1]["name"] == scenario_b["name"]
    assert pytest.report["tests"][0]["tests"][1]["text"] == scenario_b["text"]
    assert pytest.report["tests"][0]["tests"][1]["message"] == scenario_b["message"]
    assert pytest.report["tests"][0]["tests"][1]["result"] == True
    assert pytest.report["tests"][0]["tests"][1]["tests"] == []

def test_add_subtests_1_scenario_b_feature_a():
    """
        Add a test to scenario a within feature A
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_b_tests[0]["path"] = feature_a["path"]
    response = report_service.add(pytest.report_id, scenario_b_tests[0])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["message"] == "Incomplete"
    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 0
    assert len(pytest.report["tests"][2]["tests"]) == 0
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 1

    assert pytest.report["tests"][0]["tests"][1]["tests"][0]["path"] == scenario_b_tests[0]["path"]
    assert pytest.report["tests"][0]["tests"][1]["tests"][0]["test"] == scenario_b_tests[0]["test"]
    assert pytest.report["tests"][0]["tests"][1]["tests"][0]["text"] == scenario_b_tests[0]["text"]
    assert pytest.report["tests"][0]["tests"][1]["tests"][0]["result"] == scenario_b_tests[0]["result"]
    assert pytest.report["tests"][0]["tests"][1]["tests"][0]["message"] == scenario_b_tests[0]["message"]

def test_add_subtests_2_scenario_b_feature_a():
    """
        Add a test to scenario a within feature a
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_b_tests[1]["path"] = feature_a["path"]
    response = report_service.add(pytest.report_id, scenario_b_tests[1])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["message"] == "Incomplete"
    assert pytest.report["tests"][0]["message"] == "Incomplete"
    assert pytest.report["tests"][0]["result"] == None
    assert pytest.report["tests"][1]["message"] == "Incomplete"
    assert pytest.report["tests"][1]["result"] == None
    assert pytest.report["tests"][2]["message"] == "Incomplete"
    assert pytest.report["tests"][2]["result"] == None
    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 0
    assert len(pytest.report["tests"][2]["tests"]) == 0
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 2

    assert pytest.report["tests"][0]["tests"][1]["tests"][1]["path"] == scenario_b_tests[1]["path"]
    assert pytest.report["tests"][0]["tests"][1]["tests"][1]["test"] == scenario_b_tests[1]["test"]
    assert pytest.report["tests"][0]["tests"][1]["tests"][1]["text"] == scenario_b_tests[1]["text"]
    assert pytest.report["tests"][0]["tests"][1]["tests"][1]["result"] == scenario_b_tests[1]["result"]
    assert pytest.report["tests"][0]["tests"][1]["tests"][1]["message"] == scenario_b_tests[1]["message"]

def test_add_scenario_a_feature_b():
    """
        Add scenario a to feature a
        Verify it was added
    """
    scenario_a["path"] = feature_b["path"]
    response = report_service.add(pytest.report_id, scenario_a)
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["message"] == "Incomplete"
    assert pytest.report["tests"][0]["message"] == "Incomplete"
    assert pytest.report["tests"][0]["result"] == None
    assert pytest.report["tests"][1]["message"] == "Incomplete"
    assert pytest.report["tests"][1]["result"] == None
    assert pytest.report["tests"][2]["message"] == "Incomplete"
    assert pytest.report["tests"][2]["result"] == None
    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 1
    assert len(pytest.report["tests"][2]["tests"]) == 0
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][0]["tests"]) == 0

    assert pytest.report["tests"][1]["tests"][0]["_type"] == scenario_a["_type"]
    assert pytest.report["tests"][1]["tests"][0]["name"] == scenario_a["name"]
    assert pytest.report["tests"][1]["tests"][0]["text"] == scenario_a["text"]
    assert pytest.report["tests"][1]["tests"][0]["message"] == "Success"
    assert pytest.report["tests"][1]["tests"][0]["result"] == True
    assert pytest.report["tests"][1]["tests"][0]["tests"] == []

def test_add_subtests_1_scenario_a_feature_b():
    """
        Add a test to scenario a within feature a
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_a_tests[0]["path"] = feature_b["path"]
    response = report_service.add(pytest.report_id, scenario_a_tests[0])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["message"] == "Incomplete"
    assert pytest.report["tests"][0]["message"] == "Incomplete"
    assert pytest.report["tests"][0]["result"] == None
    assert pytest.report["tests"][1]["message"] == "Incomplete"
    assert pytest.report["tests"][1]["result"] == None
    assert pytest.report["tests"][2]["message"] == "Incomplete"
    assert pytest.report["tests"][2]["result"] == None
    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 1
    assert len(pytest.report["tests"][2]["tests"]) == 0
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][0]["tests"]) == 1

    assert pytest.report["tests"][1]["tests"][0]["tests"][0]["path"] == scenario_a_tests[0]["path"]
    assert pytest.report["tests"][1]["tests"][0]["tests"][0]["test"] == scenario_a_tests[0]["test"]
    assert pytest.report["tests"][1]["tests"][0]["tests"][0]["text"] == scenario_a_tests[0]["text"]
    assert pytest.report["tests"][1]["tests"][0]["tests"][0]["result"] == scenario_a_tests[0]["result"]
    assert pytest.report["tests"][1]["tests"][0]["tests"][0]["message"] == scenario_a_tests[0]["message"]

def test_add_subtests_2_scenario_a_feature_b():
    """
        Add a test to scenario a within feature a
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_a_tests[1]["path"] = feature_b["path"]
    response = report_service.add(pytest.report_id, scenario_a_tests[1])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert "end" not in pytest.report
    assert pytest.report["message"] == "Failure"
    assert pytest.report["result"] == False
    assert pytest.report["tests"][0]["message"] == "Incomplete"
    assert pytest.report["tests"][0]["result"] == None
    assert pytest.report["tests"][1]["message"] == "Failure"
    assert pytest.report["tests"][1]["result"] == False
    assert pytest.report["tests"][2]["message"] == "Incomplete"
    assert pytest.report["tests"][2]["result"] == None
    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 1
    assert len(pytest.report["tests"][2]["tests"]) == 0
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][0]["tests"]) == 2

    assert pytest.report["tests"][1]["tests"][0]["tests"][1]["path"] == scenario_a_tests[1]["path"]
    assert pytest.report["tests"][1]["tests"][0]["tests"][1]["test"] == scenario_a_tests[1]["test"]
    assert pytest.report["tests"][1]["tests"][0]["tests"][1]["text"] == scenario_a_tests[1]["text"]
    assert pytest.report["tests"][1]["tests"][0]["tests"][1]["result"] == scenario_a_tests[1]["result"]
    assert pytest.report["tests"][1]["tests"][0]["tests"][1]["message"] == scenario_a_tests[1]["message"]

def test_add_scenario_b_feature_b():
    """
        Add scenario a to feature a
        Verify it was added
    """
    scenario_b["path"] = feature_b["path"]
    response = report_service.add(pytest.report_id, scenario_b)
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert "end" not in pytest.report
    assert pytest.report["message"] == "Failure"
    assert pytest.report["result"] == False
    assert pytest.report["tests"][0]["message"] == "Incomplete"
    assert pytest.report["tests"][0]["result"] == None
    assert pytest.report["tests"][1]["message"] == "Failure"
    assert pytest.report["tests"][1]["result"] == False
    assert pytest.report["tests"][2]["message"] == "Incomplete"
    assert pytest.report["tests"][2]["result"] == None
    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][2]["tests"]) == 0
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][1]["tests"]) == 0

    assert pytest.report["tests"][1]["tests"][1]["_type"] == scenario_b["_type"]
    assert pytest.report["tests"][1]["tests"][1]["name"] == scenario_b["name"]
    assert pytest.report["tests"][1]["tests"][1]["text"] == scenario_b["text"]
    assert pytest.report["tests"][1]["tests"][1]["message"] == scenario_b["message"]
    assert pytest.report["tests"][1]["tests"][1]["result"] == True
    assert pytest.report["tests"][1]["tests"][1]["tests"] == []

def test_add_subtests_1_scenario_b_feature_b():
    """
        Add a test to scenario a within feature a
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_b_tests[0]["path"] = feature_b["path"]
    response = report_service.add(pytest.report_id, scenario_b_tests[0])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert "end" not in pytest.report
    assert pytest.report["message"] == "Failure"
    assert pytest.report["result"] == False
    assert pytest.report["tests"][0]["message"] == "Incomplete"
    assert pytest.report["tests"][0]["result"] == None
    assert pytest.report["tests"][1]["message"] == "Failure"
    assert pytest.report["tests"][1]["result"] == False
    assert pytest.report["tests"][2]["message"] == "Incomplete"
    assert pytest.report["tests"][2]["result"] == None
    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][2]["tests"]) == 0
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][1]["tests"]) == 1

    assert pytest.report["tests"][1]["tests"][1]["tests"][0]["path"] == scenario_b_tests[0]["path"]
    assert pytest.report["tests"][1]["tests"][1]["tests"][0]["test"] == scenario_b_tests[0]["test"]
    assert pytest.report["tests"][1]["tests"][1]["tests"][0]["text"] == scenario_b_tests[0]["text"]
    assert pytest.report["tests"][1]["tests"][1]["tests"][0]["result"] == scenario_b_tests[0]["result"]
    assert pytest.report["tests"][1]["tests"][1]["tests"][0]["message"] == scenario_b_tests[0]["message"]

def test_add_subtests_2_scenario_b_feature_b():
    """
        Add a test to scenario a within feature a
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_b_tests[1]["path"] = feature_b["path"]
    response = report_service.add(pytest.report_id, scenario_b_tests[1])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert "end" not in pytest.report
    assert pytest.report["message"] == "Failure"
    assert pytest.report["result"] == False
    assert pytest.report["tests"][0]["message"] == "Incomplete"
    assert pytest.report["tests"][0]["result"] == None
    assert pytest.report["tests"][1]["message"] == "Failure"
    assert pytest.report["tests"][1]["result"] == False
    assert pytest.report["tests"][2]["message"] == "Incomplete"
    assert pytest.report["tests"][2]["result"] == None
    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][2]["tests"]) == 0
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][1]["tests"]) == 2

    assert pytest.report["tests"][1]["tests"][1]["tests"][1]["path"] == scenario_b_tests[1]["path"]
    assert pytest.report["tests"][1]["tests"][1]["tests"][1]["test"] == scenario_b_tests[1]["test"]
    assert pytest.report["tests"][1]["tests"][1]["tests"][1]["text"] == scenario_b_tests[1]["text"]
    assert pytest.report["tests"][1]["tests"][1]["tests"][1]["result"] == scenario_b_tests[1]["result"]
    assert pytest.report["tests"][1]["tests"][1]["tests"][1]["message"] == scenario_b_tests[1]["message"]

def test_add_scenario_a_feature_c():
    """
        Add scenario a to feature a
        Verify it was added
    """
    scenario_a["path"] = feature_c["path"]
    response = report_service.add(pytest.report_id, scenario_a)
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert "end" not in pytest.report
    assert pytest.report["message"] == "Failure"
    assert pytest.report["result"] == False
    assert pytest.report["tests"][0]["message"] == "Incomplete"
    assert pytest.report["tests"][0]["result"] == None
    assert pytest.report["tests"][1]["message"] == "Failure"
    assert pytest.report["tests"][1]["result"] == False
    assert pytest.report["tests"][2]["message"] == "Incomplete"
    assert pytest.report["tests"][2]["result"] == None
    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][2]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][2]["tests"]) == 1
    assert len(pytest.report["tests"][2]["tests"][0]["tests"]) == 0

    assert pytest.report["tests"][2]["tests"][0]["_type"] == scenario_a["_type"]
    assert pytest.report["tests"][2]["tests"][0]["name"] == scenario_a["name"]
    assert pytest.report["tests"][2]["tests"][0]["text"] == scenario_a["text"]
    assert pytest.report["tests"][2]["tests"][0]["message"] == "Success"
    assert pytest.report["tests"][2]["tests"][0]["result"] == True
    assert pytest.report["tests"][2]["tests"][0]["tests"] == []

def test_finish_feature_a():
    """
        Finish Feature A
    """
    response = report_service.finish(pytest.report_id, feature_a["path"])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert "end" not in pytest.report
    assert pytest.report["message"] == "Failure"
    assert pytest.report["result"] == False
    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][2]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][1]["tests"]) == 2

    assert pytest.report["tests"][0]["end"]
    assert pytest.report["tests"][0]["message"] == "Success"
    assert pytest.report["tests"][0]["result"] == True

    assert pytest.report["tests"][1]["message"] == "Failure"
    assert pytest.report["tests"][1]["result"] == False

    assert "end" not in pytest.report["tests"][2]
    assert pytest.report["tests"][2]["result"] == None
    assert pytest.report["tests"][2]["message"] == "Incomplete"

def test_add_subtests_1_scenario_a_feature_c():
    """
        Add scenario a to feature a
        Verify it was added
    """
    scenario_a_tests[0]["path"] = feature_c["path"]
    response = report_service.add(pytest.report_id, scenario_a_tests[0])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert "end" not in pytest.report
    assert pytest.report["message"] == "Failure"
    assert pytest.report["result"] == False
    assert pytest.report["tests"][0]["end"]
    assert pytest.report["tests"][0]["message"] == "Success"
    assert pytest.report["tests"][0]["result"] == True
    assert pytest.report["tests"][1]["message"] == "Failure"
    assert pytest.report["tests"][1]["result"] == False
    assert pytest.report["tests"][2]["message"] == "Incomplete"
    assert pytest.report["tests"][2]["result"] == None

    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][2]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][2]["tests"]) == 1
    assert len(pytest.report["tests"][2]["tests"][0]["tests"]) == 1

    assert pytest.report["tests"][2]["tests"][0]["tests"][0]["path"] == scenario_a_tests[0]["path"]
    assert pytest.report["tests"][2]["tests"][0]["tests"][0]["test"] == scenario_a_tests[0]["test"]
    assert pytest.report["tests"][2]["tests"][0]["tests"][0]["text"] == scenario_a_tests[0]["text"]
    assert pytest.report["tests"][2]["tests"][0]["tests"][0]["result"] == scenario_a_tests[0]["result"]
    assert pytest.report["tests"][2]["tests"][0]["tests"][0]["message"] == scenario_a_tests[0]["message"]

def test_finish_feature_b():
    """
        Finish Feature B
    """
    response = report_service.finish(pytest.report_id, feature_b["path"])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert "end" not in pytest.report
    assert pytest.report["message"] == "Failure"
    assert pytest.report["result"] == False
    assert pytest.report["tests"][0]["end"]
    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][2]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][1]["tests"]) == 2

    assert pytest.report["tests"][0]["end"]
    assert pytest.report["tests"][0]["message"] == "Success"
    assert pytest.report["tests"][0]["result"] == True

    assert pytest.report["tests"][1]["end"]
    assert pytest.report["tests"][1]["message"] == "Failure"
    assert pytest.report["tests"][1]["result"] == False

    assert "end" not in pytest.report["tests"][2]
    assert pytest.report["tests"][2]["result"] == None
    assert pytest.report["tests"][2]["message"] == "Incomplete"

def test_finish_feature_c():
    """
        Finish Feature C
    """
    response = report_service.finish(pytest.report_id, feature_c["path"])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["message"] == "Failure"
    assert pytest.report["result"] == False
    assert pytest.report["end"]
    assert len(pytest.report["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][2]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["tests"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["tests"][1]["tests"][1]["tests"]) == 2

    assert pytest.report["tests"][0]["end"]
    assert pytest.report["tests"][0]["message"] == "Success"
    assert pytest.report["tests"][0]["result"] == True

    assert pytest.report["tests"][1]["end"]
    assert pytest.report["tests"][1]["message"] == "Failure"
    assert pytest.report["tests"][1]["result"] == False

    assert pytest.report["tests"][2]["end"]
    assert pytest.report["tests"][2]["message"] == "Success"
    assert pytest.report["tests"][2]["result"] == True
