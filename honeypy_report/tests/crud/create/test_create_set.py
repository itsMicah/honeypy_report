import pytest
from copy import deepcopy

from honeypy_report.tests.crud.create import (
    DEFAULT_SET_REPORT,
    FEATURES
)
from honeypy.tests.assertions.report import ReportAssertions
from honeypy.api.report import ReportService
from honeypy.api.test import TestService

def pytest_namespace():
    """
        Define pytest variables
    """
    return {
        "set_report": {},
        "feature_report_a_id":None,
        "feature_report_b_id":None,
        "feature_report_c_id":None
    }

def setup_module(module):
    """
        Instantiate variables
    """
    global report_service
    global test_service
    global assertions
    global _set

    report_service = ReportService()
    test_service = TestService()
    assertions = ReportAssertions()
    _set = DEFAULT_SET_REPORT
    add_features()
    create_features()

def add_features():
    """
        Add features to set report
    """
    _set.pop("reports")
    _set["features"].append(FEATURES[0]["path"])
    _set["features"].append(FEATURES[1]["path"])
    _set["features"].append(FEATURES[2]["path"])

def create_features():
    """
        Create feature test data
    """
    for feature in FEATURES:
        test_service.delete(feature["path"], feature["kind"])
        test_service.create(feature)


class TestCreateSet:
    """
        Verify the scenario to create a set report

        URL: "/"
        METHOD: POST
    """

    def test_set_report_with_features(self):
        """
            Create a set with features a part of the set
            Verify feature reports are created for each feature in the set
        """
        response = report_service.create(_set)

        print(response.json())
        assert response.status_code == 201

        set_report_id = response.json()["id"]
        pytest.set_report = report_service.get(set_report_id).json()
        assert all(item in pytest.set_report.items() for item in _set.items())

    def test_feature_a_report(self):
        """
            Verify the first feature report within the set report
        """
        report = pytest.set_report["reports"][0]
        pytest.feature_report_a_id = report["_id"]
        response = report_service.get(pytest.feature_report_a_id)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == report["message"]
        assert data["fail"] == report["fail"]
        assert data["browser"] == report["browser"]
        assert data["url"] == report["url"]
        assert data["host"] == report["host"]
        assert data["status"] == report["status"]
        assert data["result"] == report["result"]
        assert data["_id"] == report["_id"]
        assert data["parentId"] == pytest.set_report["_id"]

    def test_feature_b_report(self):
        """
            Verify the second feature report within the set report
        """
        report = pytest.set_report["reports"][1]
        pytest.feature_report_b_id = report["_id"]
        response = report_service.get(pytest.feature_report_b_id)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == report["message"]
        assert data["status"] == report["status"]
        assert data["result"] == report["result"]
        assert data["_id"] == report["_id"]
        assert data["fail"] == report["fail"]
        assert data["browser"] == report["browser"]
        assert data["url"] == report["url"]
        assert data["host"] == report["host"]
        assert data["parentId"] == pytest.set_report["_id"]

    def test_feature_c_report(self):
        """
            Verify the third feature report within the set report
        """
        report = pytest.set_report["reports"][2]
        pytest.feature_report_c_id = report["_id"]
        response = report_service.get(pytest.feature_report_c_id)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == report["message"]
        assert data["status"] == report["status"]
        assert data["result"] == report["result"]
        assert data["_id"] == report["_id"]
        assert data["fail"] == report["fail"]
        assert data["browser"] == report["browser"]
        assert data["url"] == report["url"]
        assert data["host"] == report["host"]
        assert data["parentId"] == pytest.set_report["_id"]
