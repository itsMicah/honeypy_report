import pytest

from honeypy_report.tests.feature_report.start_feature_report import FEATURE
from honeypy.api.report import ReportService
from honeypy.api.test import TestService

def setup_module(module):
    """
        Instantiate variables
    """
    global test_service
    global report_service
    global feature
    global report_id

    test_service = TestService()
    report_service = ReportService()
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

    def test_default_status(self):
        """
            Verify the default status of a report
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()
        assert report["status"] == "Queued"
        assert report["result"] == None

    def test_start_report(self):
        """
            Verify the ability to start a report
        """
        response = report_service.status("start", report_id)
        assert response.status_code == 204

    def test_running_status(self):
        """
            Verify the report status was updated to 'running'
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        report = response.json()
        assert report["status"] == "Running"
        assert report["result"] == None
