import pytest

from honeypy_report.tests.crud.create import (
    DEFAULT_FEATURE_REPORT,
    DEFAULT_SET_REPORT
)
from honeypy.tests.assertions.report import ReportAssertions
from honeypy.api.report import ReportService

def setup_module(module):
    """
        Instantiate variables
    """
    global report_service
    global assertions
    global expected_report
    global report_id
    global report

    report_service = ReportService()
    assertions = ReportAssertions()

class TestCreateDefault:
    """
        Verify Report Default Values

        URL: "/"
        METHOD: POST
    """

    def test_default_feature_report(self):
        """
            Create a feature report while only supplying
            the minimum required values
        """
        expected_report = {
            "kind":"feature",
            "name":"test_create_variations.py",
            "path":"test_create_variations.py",
            "contents": []
        }
        response = report_service.create(expected_report)
        assert response.status_code == 201

        report_id = response.json()["id"]
        report = report_service.get(report_id).json()

        assert all(item in report.items() for item in DEFAULT_FEATURE_REPORT.items())

    def test_default_set_report(self):
        """
            Create a set report while only supplying
            the minimum required values
        """
        expected_report = {
            "kind":"set",
            "name":"test_create_variations.py"
        }
        response = report_service.create(expected_report)
        assert response.status_code == 201

        report_id = response.json()["id"]
        report = report_service.get(report_id).json()
        assert all(item in report.items() for item in DEFAULT_SET_REPORT.items())
