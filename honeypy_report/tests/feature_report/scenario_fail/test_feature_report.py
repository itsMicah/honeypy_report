import pytest
from copy import deepcopy

from honeypy.tests.assertions.report import ReportAssertions

from honeypy_report.tests.feature_report.scenario_fail import (
    FEATURE,
    REPORT,

    SCENARIO_ID_1,
    SCENARIO_1,
    SCENARIO_1_STEPS,

    SCENARIO_ID_2,
    SCENARIO_2,
    SCENARIO_2_STEPS,
)

from honeypy.api.report import ReportService
from honeypy.api.test import TestService

def setup_module(module):
    """
        Instantiate variables
    """
    global test_service
    global report_service
    global assertions
    global feature
    global report_id

    test_service = TestService()
    report_service = ReportService()
    assertions = ReportAssertions()
    feature = setup_feature(test_service, report_service)
    report_id = create_report(report_service)

def setup_feature(test_service, report_service):
    """
        Setup feature file
    """
    test_service.delete(FEATURE["path"], "feature")
    response = test_service.create(FEATURE)
    assert response.status_code == 201
    response = test_service.get(FEATURE["path"], "feature")
    assert response.status_code == 200
    return response.json()

def create_report(report_service):
    """
        Create a report
    """
    response = report_service.create(feature)
    assert response.status_code == 201
    return response.json()["id"]

class Test:

    def test_add_scenario_1(self):
        """
            Add a single scenario to the report
        """
        response = report_service.add(report_id, SCENARIO_1)
        assert response.status_code == 204

    def test_verify_added_scenario_1(self):
        """
            Verify the scenario was added to the report
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tests"]) == 1
        assertions.assert_scenario(data["tests"][0], SCENARIO_1)

    def test_add_scenario_1_step_1(self):
        """
            Add a step to the first scenario
        """
        response = report_service.add(report_id, SCENARIO_1_STEPS[0])
        assert response.status_code == 204

    def test_verify_added_scenario_1_step_1(self):
        """
            Verify the step was added to the correct scenario
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tests"]) == 1
        assert len(data["tests"][0]["tests"]) == 1
        assertions.assert_report_result(data["tests"][0], SCENARIO_1["result"], SCENARIO_1["message"])
        assert data["tests"][0]["tests"][0]["scenarioId"] == SCENARIO_1_STEPS[0]["scenarioId"]
        assertions.assert_step(data["tests"][0]["tests"][0], SCENARIO_1_STEPS[0])

    def test_add_scenario_1_step_2(self):
        """
            Add another subtest to the first scenario
        """
        response = report_service.add(report_id, SCENARIO_1_STEPS[1])
        assert response.status_code == 204

    def test_verify_added_scenario_1_step_2(self):
        """
            Verify the step was added successfully
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tests"]) == 1
        assert len(data["tests"][0]["tests"]) == 2
        assertions.assert_report_result(data["tests"][0], SCENARIO_1["result"], SCENARIO_1["message"])
        assert data["tests"][0]["tests"][1]["scenarioId"] == SCENARIO_1_STEPS[1]["scenarioId"]
        assertions.assert_step(data["tests"][0]["tests"][1], SCENARIO_1_STEPS[1])


    def test_add_scenario_1_step_3(self):
        """
            Add another subtest to the scenario
        """
        response = report_service.add(report_id, SCENARIO_1_STEPS[2])
        assert response.status_code == 204

    def test_verify_added_scenario_1_step_3(self):
        """
            Verify the step was added to the report
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tests"]) == 1
        assert len(data["tests"][0]["tests"]) == 3
        assertions.assert_report_result(data["tests"][0], SCENARIO_1["result"], SCENARIO_1["message"])
        assert data["tests"][0]["tests"][2]["scenarioId"] == SCENARIO_1_STEPS[2]["scenarioId"]
        assertions.assert_step(data["tests"][0]["tests"][2], SCENARIO_1_STEPS[2])

    def test_add_scenario_2(self):
        """
            Add a second scenario
        """
        response = report_service.add(report_id, SCENARIO_2)
        assert response.status_code == 204

    def test_verify_added_scenario_2(self):
        """
            Verify the added scenario
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tests"]) == 2
        assertions.assert_scenario(data["tests"][1], SCENARIO_2)

    def test_add_scenario_2_step_1(self):
        """
            Add a step to the second scenario
        """
        response = report_service.add(report_id, SCENARIO_2_STEPS[0])
        assert response.status_code == 204

    def test_verify_added_scenario_2_step_1(self):
        """
            Verify the step was added to the second scenario
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tests"]) == 2
        assert len(data["tests"][1]["tests"]) == 1
        assertions.assert_report_result(data["tests"][1], SCENARIO_2["result"], SCENARIO_2["message"])
        assert data["tests"][1]["tests"][0]["scenarioId"] == SCENARIO_2_STEPS[0]["scenarioId"]
        assertions.assert_step(data["tests"][1]["tests"][0], SCENARIO_2_STEPS[0])

    def test_add_scenario_2_step_2(self):
        """
            Add a failed step to the second scenario
        """
        print("\n\n\n == " + str(SCENARIO_2_STEPS[1]["result"]) + " ==  \n\n\n")
        response = report_service.add(report_id, SCENARIO_2_STEPS[1])
        assert response.status_code == 204

    def test_verify_added_scenario_2_step_2(self):
        """
            Verify the step was added to the second scenario
            Verify the report status changed from a Pass result to a failed result
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tests"]) == 2
        assert len(data["tests"][1]["tests"]) == 2
        assertions.assert_report_result(data, False, "Failure")
        assertions.assert_report_result(data["tests"][1], SCENARIO_2_STEPS[1]["result"], SCENARIO_2_STEPS[1]["message"])
        assertions.assert_step(data["tests"][1]["tests"][1], SCENARIO_2_STEPS[1])

    def test_finish_feature(self):
        """
            Finish the feature report
        """
        response = report_service.status("finish", report_id)
        assert response.status_code == 204

    def test_verify_finish(self):
        """
            Verify the feature report has been finished
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tests"]) == 2
        assert len(data["tests"][0]["tests"]) == 3
        assert len(data["tests"][1]["tests"]) == 2
        assertions.assert_report_result(data["tests"][0], SCENARIO_1["result"], SCENARIO_1["message"])
        assertions.assert_report_result(data["tests"][1], result = False, message = "Failure")
        assertions.assert_report_status(data, "Done", False, end = True, message = "Failure")
