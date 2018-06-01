import pytest

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

    report_service = ReportService()
    assertions = ReportAssertions()

class TestCreateValidation:
    """
        Verify Create Report Validation

        URL: "/"
        METHOD: POST
    """

    def test_empty_payload(self):
        """
            Create an empty report
        """
        report = {}
        response = report_service.create(report)
        data = response.json()
        assert response.status_code == 400
        assert data["kind"][0] == 'required field'
        assert data["name"][0] == 'required field'

    def test_invalid_kind(self):
        """
            Create a report with an invalid 'kind' value
        """
        report = {
            "kind": "badvalue"
        }
        response = report_service.create(report)
        data = response.json()
        assert response.status_code == 400
        assert data["kind"][0] == 'unallowed value badvalue'

    def test_invalid_browser(self):
        """
            Verify the 'browser' field only allows certain values
        """
        report = {
            "kind":"feature",
            "name":"test_post.py",
            "browser":"FAKEBROWSER"
        }
        response = report_service.create(report)
        data = response.json()
        assert response.status_code == 400
        assert data["browser"][0] == 'unallowed value FAKEBROWSER'

    def test_invalid_result_type(self):
        """
            Verify the 'result' field must be a boolean value
        """
        report = {
            "kind":"feature",
            "name":"test_post.py",
            "result":"badvalue"
        }
        response = report_service.create(report)
        data = response.json()
        assert response.status_code == 400
        assert data["result"][0] == "must be of boolean type"

    def test_feature_report_path_field(self):
        """
            Verify the 'path' field is required for feature reports
        """
        report = {
            "kind":"feature",
            "name":"test_post.py"
        }
        response = report_service.create(report)
        data = response.json()
        assert response.status_code == 400
        assert data["path"][0] == "required field"

    def testy_feature_report_contents_field(self):
        """
            Verify the 'contents' field is required for feature reports
        """
        report = {
            "kind":"feature",
            "name":"test_post.py",
        }
        response = report_service.create(report)
        data = response.json()
        assert response.status_code == 400
        assert data["contents"][0] == "required field"

    def test_feature_report_contents_field_type(self):
        """
            Verify the 'contents' field must be a list
        """
        report = {
            "kind":"feature",
            "name":"test_post.py",
            "contents": "test contents\nmore \n contents"
        }
        response = report_service.create(report)
        data = response.json()
        assert response.status_code == 400
        assert data["contents"][0] == "must be of list type"

    def test_set_report_features_field(self):
        """
            Verify the 'contents' field must be a list
        """
        report = {
            "kind":"feature",
            "name":"test_post.py",
            "contents": "test contents\nmore \n contents"
        }
        response = report_service.create(report)
        data = response.json()
        assert response.status_code == 400
        assert data["contents"][0] == "must be of list type"
