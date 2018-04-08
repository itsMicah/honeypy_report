import pytest
from copy import deepcopy
from honeypy_report.tests.set_report.scenario_pass import (
    FEATURE_1,
    FEATURE_2,
    FEATURE_3,

    SET,

    SCENARIO_1,
    SCENARIO_1_STEPS,

    SCENARIO_2,
    SCENARIO_2_STEPS
)
from honeypy.api.report import ReportService
from honeypy.api.test import TestService
from honeypy.api.set import SetService
from honeypy.tests.fixtures.report_assertions import ReportAssertions

def setup_module(module):
    """
        Instantiate variables
    """
    global test_service
    global report_service
    global set_service
    global assertions

    global report
    global report_id
    global feature_1_id
    global feature_2_id
    global feature_3_id
    global _set

    test_service = TestService()
    report_service = ReportService()
    set_service = SetService()
    assertions = ReportAssertions()
    feature_1_id = setup_feature(FEATURE_1, test_service, report_service)
    feature_2_id = setup_feature(FEATURE_2, test_service, report_service)
    feature_3_id = setup_feature(FEATURE_3, test_service, report_service)
    _set = create_set(SET, set_service)
    report_id = create_report(_set, report_service)
    report = get_report(report_id, report_service)
    feature_1_id = report["reports"][0]["_id"]
    feature_2_id = report["reports"][1]["_id"]
    feature_3_id = report["reports"][2]["_id"]

def setup_feature(feature, test_service, report_service):
    """
        Setup feature file
    """
    test_service.delete(feature["path"], "feature")
    response = test_service.create(feature)
    assert response.status_code == 201
    response = test_service.get(feature["path"], "feature")
    assert response.status_code == 200
    return response.json()

def create_report(feature, report_service):
    """
        Create a report
    """
    response = report_service.create(feature)
    assert response.status_code == 201
    return response.json()["id"]

def get_report(report_id, report_service):
    """
        Get a report by ID
    """
    return report_service.get(report_id).json()

def create_set(_set, set_service):
    """
        Create a set
    """
    set_service.delete(_set["name"])
    response = set_service.create(_set)
    return set_service.get(_set["name"]).json()

class Test:

    def test_add_scenario_1_feature_1(self):
        """
            Add scenario A to feature A
            Verify it was added
        """
        response = report_service.add(feature_1_id, SCENARIO_1)
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert len(report["reports"][0]["tests"]) == 1
        assert len(report["reports"][1]["tests"]) == 0
        assert len(report["reports"][2]["tests"]) == 0

        assertions.assert_scenario(report["reports"][0]["tests"][0], SCENARIO_1)

    def test_add_subtest_1_scenario_1_feature_1(self):
        """
            Add a test to scenario 1 within feature A
            Verify the test has the correct attributes
            Verify other features within the set
        """
        response = report_service.add(feature_1_id, SCENARIO_1_STEPS[0])
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert len(report["reports"][0]["tests"]) == 1
        assert len(report["reports"][1]["tests"]) == 0
        assert len(report["reports"][2]["tests"]) == 0
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1

        assertions.assert_step(report["reports"][0]["tests"][0]["tests"][0], SCENARIO_1_STEPS[0])

    def test_add_scenario_2_feature_1(self):
        """
            Add scenario B to feature A
        """
        response = report_service.add(feature_1_id, SCENARIO_2)
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 0
        assert len(report["reports"][2]["tests"]) == 0
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 0

        assertions.assert_scenario(report["reports"][0]["tests"][1], SCENARIO_2)

    def test_add_subtests_1_scenario_2_feature_1(self):
        """
            Add a test to scenario 1 within feature A
            Verify the test has the correct attributes
            Verify other features within the set
        """
        response = report_service.add(feature_1_id, SCENARIO_2_STEPS[0])
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 0
        assert len(report["reports"][2]["tests"]) == 0
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 1

        assertions.assert_step(report["reports"][0]["tests"][1]["tests"][0], SCENARIO_2_STEPS[0])

    def test_add_subtests_2_scenario_2_feature_1(self):
        """
            Add a test to scenario 1 within feature 1
            Verify the test has the correct attributes
            Verify other features within the set
        """
        response = report_service.add(feature_1_id, SCENARIO_2_STEPS[1])
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert report["reports"][0]["status"] == "Queued"
        assert report["reports"][0]["result"] == None
        assert report["reports"][1]["status"] == "Queued"
        assert report["reports"][1]["result"] == None
        assert report["reports"][2]["status"] == "Queued"
        assert report["reports"][2]["result"] == None
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 0
        assert len(report["reports"][2]["tests"]) == 0
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 2

        assertions.assert_step(report["reports"][0]["tests"][1]["tests"][1], SCENARIO_2_STEPS[1])

    def test_add_scenario_1_feature_b(self):
        """
            Add scenario 1 to feature 1
            Verify it was added
        """
        response = report_service.add(feature_2_id, SCENARIO_1)
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert report["reports"][0]["status"] == "Queued"
        assert report["reports"][0]["result"] == None
        assert report["reports"][1]["status"] == "Queued"
        assert report["reports"][1]["result"] == None
        assert report["reports"][2]["status"] == "Queued"
        assert report["reports"][2]["result"] == None
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 1
        assert len(report["reports"][2]["tests"]) == 0
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 2
        assert len(report["reports"][1]["tests"][0]["tests"]) == 0

        assertions.assert_scenario(report["reports"][1]["tests"][0], SCENARIO_1)

    def test_add_subtests_1_scenario_1_feature_b(self):
        """
            Add a test to scenario 1 within feature 1
            Verify the test has the correct attributes
            Verify other features within the set
        """
        response = report_service.add(feature_2_id, SCENARIO_1_STEPS[0])
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert report["reports"][0]["status"] == "Queued"
        assert report["reports"][0]["result"] == None
        assert report["reports"][1]["status"] == "Queued"
        assert report["reports"][1]["result"] == None
        assert report["reports"][2]["status"] == "Queued"
        assert report["reports"][2]["result"] == None
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 1
        assert len(report["reports"][2]["tests"]) == 0
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 2
        assert len(report["reports"][1]["tests"][0]["tests"]) == 1

        assertions.assert_step(report["reports"][1]["tests"][0]["tests"][0], SCENARIO_1_STEPS[0])

    def test_add_subtests_2_scenario_1_feature_b(self):
        """
            Add a test to scenario 1 within feature 1
            Verify the test has the correct attributes
            Verify other features within the set
        """
        response = report_service.add(feature_2_id, SCENARIO_1_STEPS[1])
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert report["reports"][0]["status"] == "Queued"
        assert report["reports"][0]["result"] == None
        assert report["reports"][1]["status"] == "Queued"
        assert report["reports"][1]["result"] == None
        assert report["reports"][2]["status"] == "Queued"
        assert report["reports"][2]["result"] == None
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 1
        assert len(report["reports"][2]["tests"]) == 0
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 2
        assert len(report["reports"][1]["tests"][0]["tests"]) == 2

        assertions.assert_step(report["reports"][1]["tests"][0]["tests"][1], SCENARIO_1_STEPS[1])

    def test_add_scenario_2_feature_b(self):
        """
            Add scenario 1 to feature 1
            Verify it was added
        """
        response = report_service.add(feature_2_id, SCENARIO_2)
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert report["reports"][0]["status"] == "Queued"
        assert report["reports"][0]["result"] == None
        assert report["reports"][1]["status"] == "Queued"
        assert report["reports"][1]["result"] == None
        assert report["reports"][2]["status"] == "Queued"
        assert report["reports"][2]["result"] == None
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 2
        assert len(report["reports"][2]["tests"]) == 0
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 2
        assert len(report["reports"][1]["tests"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"][1]["tests"]) == 0

        assertions.assert_scenario(report["reports"][1]["tests"][1], SCENARIO_2)

    def test_add_subtests_1_scenario_2_feature_b(self):
        """
            Add a test to scenario 1 within feature 1
            Verify the test has the correct attributes
            Verify other features within the set
        """
        response = report_service.add(feature_2_id, SCENARIO_2_STEPS[0])
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert report["reports"][0]["status"] == "Queued"
        assert report["reports"][0]["result"] == None
        assert report["reports"][1]["status"] == "Queued"
        assert report["reports"][1]["result"] == None
        assert report["reports"][2]["status"] == "Queued"
        assert report["reports"][2]["result"] == None
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 2
        assert len(report["reports"][2]["tests"]) == 0
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 2
        assert len(report["reports"][1]["tests"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"][1]["tests"]) == 1

        assertions.assert_step(report["reports"][1]["tests"][1]["tests"][0], SCENARIO_2_STEPS[0])

    def test_add_subtests_2_scenario_2_feature_b(self):
        """
            Add a test to scenario 1 within feature 1
            Verify the test has the correct attributes
            Verify other features within the set
        """
        response = report_service.add(feature_2_id, SCENARIO_2_STEPS[1])
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert report["reports"][0]["status"] == "Queued"
        assert report["reports"][0]["result"] == None
        assert report["reports"][1]["status"] == "Queued"
        assert report["reports"][1]["result"] == None
        assert report["reports"][2]["status"] == "Queued"
        assert report["reports"][2]["result"] == None
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 2
        assert len(report["reports"][2]["tests"]) == 0
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 2
        assert len(report["reports"][1]["tests"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"][1]["tests"]) == 2

        assertions.assert_step(report["reports"][1]["tests"][1]["tests"][1], SCENARIO_2_STEPS[1])

    def test_add_scenario_1_feature_c(self):
        """
            Add scenario 1 to feature 1
            Verify it was added
        """
        response = report_service.add(feature_3_id, SCENARIO_1)
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert report["reports"][0]["status"] == "Queued"
        assert report["reports"][0]["result"] == None
        assert report["reports"][1]["status"] == "Queued"
        assert report["reports"][1]["result"] == None
        assert report["reports"][2]["status"] == "Queued"
        assert report["reports"][2]["result"] == None
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 2
        assert len(report["reports"][2]["tests"]) == 1
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 2
        assert len(report["reports"][1]["tests"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"][1]["tests"]) == 2
        assert len(report["reports"][2]["tests"]) == 1
        assert len(report["reports"][2]["tests"][0]["tests"]) == 0

        assertions.assert_scenario(report["reports"][2]["tests"][0], SCENARIO_1)

    def test_finish_feature_1(self):
        """
            Finish Feature A
        """
        response = report_service.finish(feature_1_id)
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 2
        assert len(report["reports"][2]["tests"]) == 1
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 2
        assert len(report["reports"][1]["tests"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"][1]["tests"]) == 2

        assert report["reports"][0]["end"]
        assert report["reports"][0]["status"] == "Done"
        assert report["reports"][0]["message"] == "Success"
        assert report["reports"][0]["result"] == True

        assert "end" not in report["reports"][1]
        assert report["reports"][1]["result"] == None
        assert report["reports"][1]["status"] == "Queued"

        assert "end" not in report["reports"][2]
        assert report["reports"][2]["result"] == None
        assert report["reports"][2]["status"] == "Queued"

    def test_add_subtests_1_scenario_1_feature_c(self):
        """
            Add step 1 of scenario 1 to feature 3
            Verify it was added
        """
        response = report_service.add(feature_3_id, SCENARIO_1_STEPS[0])
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert report["reports"][0]["end"]
        assert report["reports"][0]["message"] == "Success"
        assert report["reports"][0]["result"] == True
        assert report["reports"][1]["status"] == "Queued"
        assert report["reports"][1]["result"] == None
        assert report["reports"][2]["status"] == "Queued"
        assert report["reports"][2]["result"] == None
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 2
        assert len(report["reports"][2]["tests"]) == 1
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 2
        assert len(report["reports"][1]["tests"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"][1]["tests"]) == 2
        assert len(report["reports"][2]["tests"]) == 1
        assert len(report["reports"][2]["tests"][0]["tests"]) == 1

        assertions.assert_step(report["reports"][2]["tests"][0]["tests"][0], SCENARIO_1_STEPS[0])

    def test_finish_feature_b(self):
        """
            Finish Feature B
        """
        response = report_service.finish(feature_2_id)
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["status"] == "Queued"
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 2
        assert len(report["reports"][2]["tests"]) == 1
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 2
        assert len(report["reports"][1]["tests"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"][1]["tests"]) == 2

        assertions.assert_report_status(report["reports"][0], "Done", True, end = True, message = "Success")
        assertions.assert_report_status(report["reports"][1], "Done", True, end = True, message = "Success")
        assertions.assert_report_status(report["reports"][2], "Queued", None)

    def test_finish_feature_c(self):
        """
            Finish Feature C
        """
        response = report_service.finish(feature_3_id)
        assert response.status_code == 204

        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()

        assert report["message"] == "Success"
        assert report["result"] == True
        assert report["end"]
        assert len(report["reports"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"]) == 2
        assert len(report["reports"][2]["tests"]) == 1
        assert len(report["reports"][0]["tests"][0]["tests"]) == 1
        assert len(report["reports"][0]["tests"][1]["tests"]) == 2
        assert len(report["reports"][1]["tests"][0]["tests"]) == 2
        assert len(report["reports"][1]["tests"][1]["tests"]) == 2

        assertions.assert_report_status(report["reports"][0], "Done", True, end = True, message = "Success")
        assertions.assert_report_status(report["reports"][1], "Done", True, end = True, message = "Success")
        assertions.assert_report_status(report["reports"][2], "Done", True, end = True, message = "Success")
