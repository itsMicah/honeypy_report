import pytest
from copy import deepcopy

from honeypy_report.tests.feature_report.step_fail import (
    FEATURE,
    REPORT,
    STEPS
)

from honeypy.tests.fixtures.report_assertions import ReportAssertions
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
        Return the report ID
    """
    response = report_service.create(feature)
    assert response.status_code == 201
    return response.json()["id"]

class Test:
    """
        Test a failed feature report
    """

    def test_add_step_1(self):
        response = report_service.add(report_id, STEPS[0])
        assert response.status_code == 204

    def test_verify_added_step_1(self):
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tests"]) == 1
        assertions.assert_step(data["tests"][0], STEPS[0])

    def test_add_step_2(self):
        response = report_service.add(report_id, STEPS[1])
        assert response.status_code == 204

    def test_verify_added_step_2(self):
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tests"]) == 2
        assertions.assert_report_result(data, False, "Failure")
        assertions.assert_step(data["tests"][1], STEPS[1])

    def test_add_step_3(self):
        response = report_service.add(report_id, STEPS[2])
        assert response.status_code == 204

    def test_verify_added_step_3(self):
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tests"]) == 3
        assertions.assert_report_result(data, False, "Failure")
        assertions.assert_step(data["tests"][2], STEPS[2])

    def test_finish_feature(self):
        response = report_service.finish(report_id)
        assert response.status_code == 204

    def test_verify_finish(self):
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tests"]) == 3
        assertions.assert_report_status(data, "Done", False, end = True, message = "Failure")
