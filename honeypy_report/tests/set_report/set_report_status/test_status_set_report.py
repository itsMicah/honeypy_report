import pytest
from honeypy_report.tests.set_report.set_report_status import (
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
from honeypy.tests.assertions.helpers import Helpers
from honeypy.tests.assertions.report import ReportAssertions

def setup_module(module):
    """
        Instantiate variables
    """
    global test_service
    global report_service
    global set_service
    global assertions
    global helpers

    global report
    global report_id
    global feature_1_id
    global feature_2_id
    global feature_3_id
    global _set

    helpers = Helpers()
    test_service = TestService()
    report_service = ReportService()
    set_service = SetService()
    assertions = ReportAssertions()
    feature_1_id = helpers.setup_feature(FEATURE_1)
    feature_2_id = helpers.setup_feature(FEATURE_2)
    feature_3_id = helpers.setup_feature(FEATURE_3)
    _set = helpers.create_set(SET)
    report_id = helpers.create_report(_set)
    report = helpers.get_report(report_id, True)
    feature_1_id = report["reports"][0]["_id"]
    feature_2_id = report["reports"][1]["_id"]
    feature_3_id = report["reports"][2]["_id"]

class Test:

    def test_default_set_status(self):
        """
            Verify the default status of a set report
        """
        assert report["status"] == "Queued"
        assert report["result"] == None
        assert report["message"] == None
        assert len(report["reports"]) == 3

    def test_default_feature_1_status(self):
        """
            Verify feature 1 status
        """
        assert report["reports"][0]["status"] == "Queued"
        assert report["reports"][0]["message"] == None
        assert report["reports"][0]["result"] == None
        assert report["reports"][0]["fail"] == False

    def test_default_feature_2_status(self):
        """
            Verify feature 2 status
        """
        assert report["reports"][1]["status"] == "Queued"
        assert report["reports"][1]["message"] == None
        assert report["reports"][1]["result"] == None
        assert report["reports"][1]["fail"] == False

    def test_default_feature_3_status(self):
        """
            Verify feature 3 status
        """
        assert report["reports"][2]["status"] == "Queued"
        assert report["reports"][2]["message"] == None
        assert report["reports"][2]["result"] == None
        assert report["reports"][2]["fail"] == False

    def test_start_feature_1(self):
        """
            Verify start feature 1
        """
        response = report_service.status("start", feature_1_id)
        assert response.status_code == 204

    def test_set_start_status_1(self):
        """
            Verify set report after starting feature 1
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Running"
        assert data["message"] == None
        assert data["result"] == None
        assert data["reports"][0]["status"] == "Running"
        assert data["reports"][0]["message"] == None
        assert data["reports"][0]["result"] == None
        assert data["reports"][0]["fail"] == False
        assert data["reports"][1]["status"] == "Queued"
        assert data["reports"][1]["message"] == None
        assert data["reports"][1]["result"] == None
        assert data["reports"][1]["fail"] == False
        assert data["reports"][2]["status"] == "Queued"
        assert data["reports"][2]["message"] == None
        assert data["reports"][2]["result"] == None
        assert data["reports"][2]["fail"] == False

    def test_feature_1_start_status_1(self):
        """
            Verify the feature 1 report
        """
        response = report_service.get(feature_1_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Running"
        assert data["message"] == None
        assert data["result"] == None

    def test_feature_2_queued_status_1(self):
        """
            Verify the feature 2 report
        """
        response = report_service.get(feature_2_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Queued"
        assert data["message"] == None
        assert data["result"] == None

    def test_feature_3_queued_status_1(self):
        """
            Verify the feature 3 report
        """
        response = report_service.get(feature_3_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Queued"
        assert data["message"] == None
        assert data["result"] == None

    def test_start_feature_2(self):
        """
            Start feature 2 report
        """
        response = report_service.status("start", feature_2_id)
        assert response.status_code == 204

    def test_set_start_feature_2_status_2(self):
        """
            Verify the set report
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Running"
        assert data["message"] == None
        assert data["result"] == None
        assert data["reports"][0]["status"] == "Running"
        assert data["reports"][0]["message"] == None
        assert data["reports"][0]["result"] == None
        assert data["reports"][0]["fail"] == False
        assert data["reports"][1]["status"] == "Running"
        assert data["reports"][1]["message"] == None
        assert data["reports"][1]["result"] == None
        assert data["reports"][1]["fail"] == False
        assert data["reports"][2]["status"] == "Queued"
        assert data["reports"][2]["message"] == None
        assert data["reports"][2]["result"] == None
        assert data["reports"][2]["fail"] == False

    def test_feature_1_start_status_2(self):
        """
            Verify feature 1 status
        """
        response = report_service.get(feature_1_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Running"
        assert data["message"] == None
        assert data["result"] == None

    def test_feature_2_queued_status_2(self):
        """
            Verify feature 2 status
        """
        response = report_service.get(feature_2_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Running"
        assert data["message"] == None
        assert data["result"] == None

    def test_feature_3_queued_status_2(self):
        """
            Verify feature 3 status
        """
        response = report_service.get(feature_3_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Queued"
        assert data["message"] == None
        assert data["result"] == None

    def test_finish_feature_1(self):
        """
            Finish feature 1
        """
        response = report_service.status("finish", feature_1_id)
        assert response.status_code == 204

    def test_set_start_feature_2_status_3(self):
        """
            Verify set report
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Running"
        assert data["message"] == None
        assert data["result"] == None
        assert data["reports"][0]["status"] == "Done"
        assert data["reports"][0]["message"] == "Success"
        assert data["reports"][0]["result"] == True
        assert data["reports"][0]["fail"] == False
        assert data["reports"][1]["status"] == "Running"
        assert data["reports"][1]["message"] == None
        assert data["reports"][1]["result"] == None
        assert data["reports"][1]["fail"] == False
        assert data["reports"][2]["status"] == "Queued"
        assert data["reports"][2]["message"] == None
        assert data["reports"][2]["result"] == None
        assert data["reports"][2]["fail"] == False

    def test_feature_1_finish_status_1(self):
        """
            Verify feature 1 status
        """
        response = report_service.get(feature_1_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Done"
        assert data["message"] == "Success"
        assert data["result"] == True

    def test_feature_2_running_status_1(self):
        """
            Verify feature 2 running status
        """
        response = report_service.get(feature_2_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Running"
        assert data["message"] == None
        assert data["result"] == None

    def test_feature_3_queued_status_3(self):
        """
            Verify feature 3 queued status
        """
        response = report_service.get(feature_3_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Queued"
        assert data["message"] == None
        assert data["result"] == None

    def test_start_feature_3(self):
        """
            Start feature 3
        """
        response = report_service.status("start", feature_3_id)
        assert response.status_code == 204

    def test_set_start_feature_2_status_4(self):
        """
            Verify set report
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Running"
        assert data["message"] == None
        assert data["result"] == None
        assert data["reports"][0]["status"] == "Done"
        assert data["reports"][0]["message"] == "Success"
        assert data["reports"][0]["result"] == True
        assert data["reports"][0]["fail"] == False
        assert data["reports"][1]["status"] == "Running"
        assert data["reports"][1]["message"] == None
        assert data["reports"][1]["result"] == None
        assert data["reports"][1]["fail"] == False
        assert data["reports"][2]["status"] == "Running"
        assert data["reports"][2]["message"] == None
        assert data["reports"][2]["result"] == None
        assert data["reports"][2]["fail"] == False

    def test_feature_1_finish_status_2(self):
        """
            Verify feature 1 done status
        """
        response = report_service.get(feature_1_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Done"
        assert data["message"] == "Success"
        assert data["result"] == True

    def test_feature_2_running_status_2(self):
        """
            Verify feature 2 running status
        """
        response = report_service.get(feature_2_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Running"
        assert data["message"] == None
        assert data["result"] == None

    def test_feature_3_running_status_1(self):
        """
            Verify feature 3 running status
        """
        response = report_service.get(feature_3_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Running"
        assert data["message"] == None
        assert data["result"] == None

    def test_finish_feature_2(self):
        """
            Finish feature 2
        """
        response = report_service.status("finish", feature_2_id)
        assert response.status_code == 204

    def test_set_start_feature_2_status_5(self):
        """
            Verify set report
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Running"
        assert data["message"] == None
        assert data["result"] == None
        assert data["reports"][0]["status"] == "Done"
        assert data["reports"][0]["message"] == "Success"
        assert data["reports"][0]["result"] == True
        assert data["reports"][1]["status"] == "Done"
        assert data["reports"][1]["message"] == "Success"
        assert data["reports"][1]["result"] == True
        assert data["reports"][2]["status"] == "Running"
        assert data["reports"][2]["message"] == None
        assert data["reports"][2]["result"] == None

    def test_feature_1_finish_status_3(self):
        """
            Verify feature 1 done status
        """
        response = report_service.get(feature_1_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Done"
        assert data["message"] == "Success"
        assert data["result"] == True

    def test_feature_2_finish_status_1(self):
        """
            Verify feature 2 finish status
        """
        response = report_service.get(feature_2_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Done"
        assert data["message"] == "Success"
        assert data["result"] == True

    def test_feature_3_running_status_2(self):
        """
            Verify feature 3 running status
        """
        response = report_service.get(feature_3_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Running"
        assert data["message"] == None
        assert data["result"] == None

    def test_finish_feature_3(self):
        """
            Finish feature 3
        """
        response = report_service.status("finish", feature_3_id)
        assert response.status_code == 204

    def test_set_start_feature_status_6(self):
        """
            Verify set report
        """
        response = report_service.get(report_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Done"
        assert data["message"] == "Success"
        assert data["result"] == True
        assert data["reports"][0]["status"] == "Done"
        assert data["reports"][0]["message"] == "Success"
        assert data["reports"][0]["result"] == True
        assert data["reports"][0]["fail"] == False
        assert data["reports"][1]["status"] == "Done"
        assert data["reports"][1]["message"] == "Success"
        assert data["reports"][1]["result"] == True
        assert data["reports"][1]["fail"] == False
        assert data["reports"][2]["status"] == "Done"
        assert data["reports"][2]["message"] == "Success"
        assert data["reports"][2]["result"] == True
        assert data["reports"][2]["fail"] == False

    def test_feature_1_finish_status_4(self):
        """
            Verify feature one finish status
        """
        response = report_service.get(feature_1_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Done"
        assert data["message"] == "Success"
        assert data["result"] == True

    def test_feature_2_finish_status_2(self):
        """
            Verify feature 2 done status
        """
        response = report_service.get(feature_2_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Done"
        assert data["message"] == "Success"
        assert data["result"] == True

    def test_feature_3_queued_status_4(self):
        """
            Verify feature 3 done status
        """
        response = report_service.get(feature_3_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Done"
        assert data["message"] == "Success"
        assert data["result"] == True
