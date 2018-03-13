import pytest
from copy import deepcopy
from honeypy.api.report import ReportService
from honeypy.api.test import TestService
from honeypy.api.set import SetService
from bson.objectid import ObjectId
from honeypy_report.tests.assertions import Assertions

# Initiate services
test_service = TestService()
set_service = SetService()
report_service = ReportService()
assertions = Assertions()

def pytest_namespace():
    return {
        'report_id': None,
        'report': {},
        '_set': {},
        "feature_a_id": None,
        "feature_b_id": None,
        "feature_c_id": None
    }

# define test feature a
feature_a = {
    "path":"feature_report_a.feature",
    "kind":"feature",
    "host":"Localhost"
}

# define test feature b
feature_b = {
    "path":"feature_report_b.feature",
    "kind":"feature",
    "host":"Localhost"
}

# define test feature c
feature_c = {
    "path":"feature_report_c.feature",
    "kind":"feature",
    "host":"Localhost"
}

# define the set
# the set should contain the features above
# the set will be used as the payload to create the set report
_set = {
    "kind": "set",
    "name": "Test Set",
    "host": "Localhost",
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
    "kind":"feature",
    "type":"scenario",
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
        "kind":"feature",
        "type":"step",
        "test":"Given I do things",
        "text":"Given I do things",
        "result": True,
        "message": "Success",
        "scenarioId": scenario_id_a
    },
    {
        "kind":"feature",
        "type":"step",
        "test":"When I do things",
        "text":"When I do things",
        "result": True,
        "message": "Pass The Things",
        "scenarioId": scenario_id_a
    },
    {
        "kind":"feature",
        "type":"step",
        "test":"Then I do things",
        "text":"Then I do things",
        "result": True,
        "message": "Success",
        "scenarioId": scenario_id_a
    }
]

# Define a scenario
scenario_b = {
    "kind":"feature",
    "type":"scenario",
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
        "kind":"feature",
        "type":"step",
        "test":"Given I do things again",
        "text":"Given I do things again",
        "result": True,
        "message": "Success",
        "scenarioId": scenario_id_b
    },
    {
        "kind":"feature",
        "type":"step",
        "test":"When I do things again",
        "text":"When I do things again",
        "result": True,
        "message": "Pass The Things",
        "scenarioId": scenario_id_b
    },
    {
        "kind":"feature",
        "type":"step",
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

def test_verify_feature_report_ids():
    """
        Get the report by ID
    """
    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()
    assert len(pytest.report["reports"]) == 3
    pytest.feature_a_id = pytest.report["reports"][0]["_id"]
    pytest.feature_b_id = pytest.report["reports"][1]["_id"]
    pytest.feature_c_id = pytest.report["reports"][2]["_id"]

def test_verify_incomplete_set_report():
    """
        Verify the set report is correct
    """
    assert not "message" in pytest.report
    assert pytest.report["status"] == "Queued"
    assert pytest.report["features"] == pytest._set["features"]
    assert pytest.report["kind"] == pytest._set["kind"]
    assert pytest.report["name"] == pytest._set["name"]
    assert len(pytest.report["reports"]) == 3

    assertions.assert_queued_feature(pytest.report["reports"][0], pytest._set["features"][0])
    assertions.assert_queued_feature(pytest.report["reports"][1], pytest._set["features"][1])
    assertions.assert_queued_feature(pytest.report["reports"][2], pytest._set["features"][2])

def test_add_scenario_a_feature_a():
    """
        Add scenario A to feature A
        Verify it was added
    """
    scenario_a["path"] = feature_a["path"]
    response = report_service.add(pytest.feature_a_id, scenario_a)
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert len(pytest.report["reports"][0]["tests"]) == 1
    assert len(pytest.report["reports"][1]["tests"]) == 0
    assert len(pytest.report["reports"][2]["tests"]) == 0

    assertions.assert_scenario(pytest.report["reports"][0]["tests"][0], scenario_a)

def test_add_subtest_1_scenario_a_feature_a():
    """
        Add a test to scenario a within feature A
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_a_tests[0]["path"] = feature_a["path"]
    response = report_service.add(pytest.feature_a_id, scenario_a_tests[0])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert len(pytest.report["reports"][0]["tests"]) == 1
    assert len(pytest.report["reports"][1]["tests"]) == 0
    assert len(pytest.report["reports"][2]["tests"]) == 0
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1

    assertions.assert_step(pytest.report["reports"][0]["tests"][0]["tests"][0], scenario_a_tests[0])

def test_add_scenario_b_feature_a():
    """
        Add scenario B to feature A
    """
    scenario_b["path"] = feature_a["path"]
    response = report_service.add(pytest.feature_a_id, scenario_b)
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 0
    assert len(pytest.report["reports"][2]["tests"]) == 0
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 0

    assertions.assert_scenario(pytest.report["reports"][0]["tests"][1], scenario_b)

def test_add_subtests_1_scenario_b_feature_a():
    """
        Add a test to scenario a within feature A
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_b_tests[0]["path"] = feature_a["path"]
    response = report_service.add(pytest.feature_a_id, scenario_b_tests[0])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 0
    assert len(pytest.report["reports"][2]["tests"]) == 0
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 1

    assertions.assert_step(pytest.report["reports"][0]["tests"][1]["tests"][0], scenario_b_tests[0])

def test_add_subtests_2_scenario_b_feature_a():
    """
        Add a test to scenario a within feature a
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_b_tests[1]["path"] = feature_a["path"]
    response = report_service.add(pytest.feature_a_id, scenario_b_tests[1])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert pytest.report["reports"][0]["status"] == "Queued"
    assert pytest.report["reports"][0]["result"] == None
    assert pytest.report["reports"][1]["status"] == "Queued"
    assert pytest.report["reports"][1]["result"] == None
    assert pytest.report["reports"][2]["status"] == "Queued"
    assert pytest.report["reports"][2]["result"] == None
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 0
    assert len(pytest.report["reports"][2]["tests"]) == 0
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 2

    assertions.assert_step(pytest.report["reports"][0]["tests"][1]["tests"][1], scenario_b_tests[1])

def test_add_scenario_a_feature_b():
    """
        Add scenario a to feature a
        Verify it was added
    """
    scenario_a["path"] = feature_b["path"]
    response = report_service.add(pytest.feature_b_id, scenario_a)
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert pytest.report["reports"][0]["status"] == "Queued"
    assert pytest.report["reports"][0]["result"] == None
    assert pytest.report["reports"][1]["status"] == "Queued"
    assert pytest.report["reports"][1]["result"] == None
    assert pytest.report["reports"][2]["status"] == "Queued"
    assert pytest.report["reports"][2]["result"] == None
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 1
    assert len(pytest.report["reports"][2]["tests"]) == 0
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][0]["tests"]) == 0

    assertions.assert_scenario(pytest.report["reports"][1]["tests"][0], scenario_a)

def test_add_subtests_1_scenario_a_feature_b():
    """
        Add a test to scenario a within feature a
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_a_tests[0]["path"] = feature_b["path"]
    response = report_service.add(pytest.feature_b_id, scenario_a_tests[0])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert pytest.report["reports"][0]["status"] == "Queued"
    assert pytest.report["reports"][0]["result"] == None
    assert pytest.report["reports"][1]["status"] == "Queued"
    assert pytest.report["reports"][1]["result"] == None
    assert pytest.report["reports"][2]["status"] == "Queued"
    assert pytest.report["reports"][2]["result"] == None
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 1
    assert len(pytest.report["reports"][2]["tests"]) == 0
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][0]["tests"]) == 1

    assertions.assert_step(pytest.report["reports"][1]["tests"][0]["tests"][0], scenario_a_tests[0])

def test_add_subtests_2_scenario_a_feature_b():
    """
        Add a test to scenario a within feature a
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_a_tests[1]["path"] = feature_b["path"]
    response = report_service.add(pytest.feature_b_id, scenario_a_tests[1])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert pytest.report["reports"][0]["status"] == "Queued"
    assert pytest.report["reports"][0]["result"] == None
    assert pytest.report["reports"][1]["status"] == "Queued"
    assert pytest.report["reports"][1]["result"] == None
    assert pytest.report["reports"][2]["status"] == "Queued"
    assert pytest.report["reports"][2]["result"] == None
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 1
    assert len(pytest.report["reports"][2]["tests"]) == 0
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][0]["tests"]) == 2

    assertions.assert_step(pytest.report["reports"][1]["tests"][0]["tests"][1], scenario_a_tests[1])

def test_add_scenario_b_feature_b():
    """
        Add scenario a to feature a
        Verify it was added
    """
    scenario_b["path"] = feature_b["path"]
    response = report_service.add(pytest.feature_b_id, scenario_b)
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert pytest.report["reports"][0]["status"] == "Queued"
    assert pytest.report["reports"][0]["result"] == None
    assert pytest.report["reports"][1]["status"] == "Queued"
    assert pytest.report["reports"][1]["result"] == None
    assert pytest.report["reports"][2]["status"] == "Queued"
    assert pytest.report["reports"][2]["result"] == None
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 2
    assert len(pytest.report["reports"][2]["tests"]) == 0
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][1]["tests"]) == 0

    assertions.assert_scenario(pytest.report["reports"][1]["tests"][1], scenario_b)

def test_add_subtests_1_scenario_b_feature_b():
    """
        Add a test to scenario a within feature a
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_b_tests[0]["path"] = feature_b["path"]
    response = report_service.add(pytest.feature_b_id, scenario_b_tests[0])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert pytest.report["reports"][0]["status"] == "Queued"
    assert pytest.report["reports"][0]["result"] == None
    assert pytest.report["reports"][1]["status"] == "Queued"
    assert pytest.report["reports"][1]["result"] == None
    assert pytest.report["reports"][2]["status"] == "Queued"
    assert pytest.report["reports"][2]["result"] == None
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 2
    assert len(pytest.report["reports"][2]["tests"]) == 0
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][1]["tests"]) == 1

    assertions.assert_step(pytest.report["reports"][1]["tests"][1]["tests"][0], scenario_b_tests[0])

def test_add_subtests_2_scenario_b_feature_b():
    """
        Add a test to scenario a within feature a
        Verify the test has the correct attributes
        Verify other features within the set
    """
    scenario_b_tests[1]["path"] = feature_b["path"]
    response = report_service.add(pytest.feature_b_id, scenario_b_tests[1])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert pytest.report["reports"][0]["status"] == "Queued"
    assert pytest.report["reports"][0]["result"] == None
    assert pytest.report["reports"][1]["status"] == "Queued"
    assert pytest.report["reports"][1]["result"] == None
    assert pytest.report["reports"][2]["status"] == "Queued"
    assert pytest.report["reports"][2]["result"] == None
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 2
    assert len(pytest.report["reports"][2]["tests"]) == 0
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][1]["tests"]) == 2

    assertions.assert_step(pytest.report["reports"][1]["tests"][1]["tests"][1], scenario_b_tests[1])

def test_add_scenario_a_feature_c():
    """
        Add scenario a to feature a
        Verify it was added
    """
    scenario_a["path"] = feature_c["path"]
    response = report_service.add(pytest.feature_c_id, scenario_a)
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert pytest.report["reports"][0]["status"] == "Queued"
    assert pytest.report["reports"][0]["result"] == None
    assert pytest.report["reports"][1]["status"] == "Queued"
    assert pytest.report["reports"][1]["result"] == None
    assert pytest.report["reports"][2]["status"] == "Queued"
    assert pytest.report["reports"][2]["result"] == None
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 2
    assert len(pytest.report["reports"][2]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][1]["tests"]) == 2
    assert len(pytest.report["reports"][2]["tests"]) == 1
    assert len(pytest.report["reports"][2]["tests"][0]["tests"]) == 0

    assertions.assert_scenario(pytest.report["reports"][2]["tests"][0], scenario_a)

def test_finish_feature_a():
    """
        Finish Feature A
    """
    response = report_service.finish(pytest.feature_a_id, feature_a["path"])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 2
    assert len(pytest.report["reports"][2]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][1]["tests"]) == 2

    assert pytest.report["reports"][0]["end"]
    assert pytest.report["reports"][0]["status"] == "Done"
    assert pytest.report["reports"][0]["message"] == "Success"
    assert pytest.report["reports"][0]["result"] == True

    assert "end" not in pytest.report["reports"][1]
    assert pytest.report["reports"][1]["result"] == None
    assert pytest.report["reports"][1]["status"] == "Queued"

    assert "end" not in pytest.report["reports"][2]
    assert pytest.report["reports"][2]["result"] == None
    assert pytest.report["reports"][2]["status"] == "Queued"

def test_add_subtests_1_scenario_a_feature_c():
    """
        Add sub test 1 of scenario a to feature c
        Verify it was added
    """
    scenario_a_tests[0]["path"] = feature_c["path"]
    response = report_service.add(pytest.feature_c_id, scenario_a_tests[0])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert pytest.report["reports"][0]["end"]
    assert pytest.report["reports"][0]["message"] == "Success"
    assert pytest.report["reports"][0]["result"] == True
    assert pytest.report["reports"][1]["status"] == "Queued"
    assert pytest.report["reports"][1]["result"] == None
    assert pytest.report["reports"][2]["status"] == "Queued"
    assert pytest.report["reports"][2]["result"] == None
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 2
    assert len(pytest.report["reports"][2]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][1]["tests"]) == 2
    assert len(pytest.report["reports"][2]["tests"]) == 1
    assert len(pytest.report["reports"][2]["tests"][0]["tests"]) == 1

    assertions.assert_step(pytest.report["reports"][2]["tests"][0]["tests"][0], scenario_a_tests[0])

def test_finish_feature_b():
    """
        Finish Feature B
    """
    response = report_service.finish(pytest.feature_b_id, feature_b["path"])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["status"] == "Queued"
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 2
    assert len(pytest.report["reports"][2]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][1]["tests"]) == 2

    assertions.assert_report_status(pytest.report["reports"][0], "Done", True, end = True, message = "Success")
    assertions.assert_report_status(pytest.report["reports"][1], "Done", True, end = True, message = "Success")
    assertions.assert_report_status(pytest.report["reports"][2], "Queued", None)

def test_finish_feature_c():
    """
        Finish Feature C
    """
    response = report_service.finish(pytest.feature_c_id, feature_c["path"])
    assert response.status_code == 204

    response = report_service.get(pytest.report_id)
    assert response.status_code == 200
    pytest.report = response.json()

    assert pytest.report["message"] == "Success"
    assert pytest.report["result"] == True
    assert pytest.report["end"]
    assert len(pytest.report["reports"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"]) == 2
    assert len(pytest.report["reports"][2]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][0]["tests"]) == 1
    assert len(pytest.report["reports"][0]["tests"][1]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][0]["tests"]) == 2
    assert len(pytest.report["reports"][1]["tests"][1]["tests"]) == 2

    assertions.assert_report_status(pytest.report["reports"][0], "Done", True, end = True, message = "Success")
    assertions.assert_report_status(pytest.report["reports"][1], "Done", True, end = True, message = "Success")
    assertions.assert_report_status(pytest.report["reports"][2], "Done", True, end = True, message = "Success")
