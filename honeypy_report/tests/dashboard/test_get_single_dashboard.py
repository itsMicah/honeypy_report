import pytest
from copy import deepcopy
from honeypy_report.tests.dashboard import (
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
from honeypy.tests.assertions.report import ReportAssertions
from honeypy.common import Common
from honeypy.tests.assertions.helpers import Helpers

def setup_module(module):
    """
        Instantiate variables
    """
    global test_service
    global report_service
    global set_service
    global assertions
    global common
    global helpers

    global set_report
    global set_report_id
    global feature_1_id
    global feature_2_id
    global feature_3_id
    global _set
    global dashboard

    helpers = Helpers()
    common = Common()
    test_service = TestService()
    report_service = ReportService()
    set_service = SetService()
    assertions = ReportAssertions()
    feature_1_id = helpers.setup_feature(FEATURE_1)
    feature_2_id = helpers.setup_feature(FEATURE_2)
    feature_3_id = helpers.setup_feature(FEATURE_3)
    _set = helpers.create_set(SET)
    set_report_id = helpers.create_report(_set)
    set_report = helpers.get_report(set_report_id, True)
    feature_1_id = set_report["reports"][0]["_id"]
    feature_2_id = set_report["reports"][1]["_id"]
    feature_3_id = set_report["reports"][2]["_id"]
    query = {"environment":SET["environment"]}
    dashboard = helpers.get_dashboard(query)

class Test:

    def test_dashboard_response(self):
        """
            Get a dashboard
        """
        assert len(dashboard) == 1
        assert dashboard[_set["name"]]
        assert dashboard[_set["name"]]["firefox"] == []
        assert dashboard[_set["name"]]["safari"] == []
        assert dashboard[_set["name"]]["edge"] == []
        assert dashboard[_set["name"]]["ie11"] == []
        assert len(dashboard[_set["name"]]["chrome"]) == 1

    def test_dashboard_set_result(self):
        set_instance = dashboard[_set["name"]]["chrome"][0]
        assert set_instance["_id"] == _set["name"]
        assert set_instance["browser"] == _set["browser"]
        assert set_instance["environment"]["name"] == _set["environment"]
        assert set_instance["host"] == _set["host"]
        assert set_instance["kind"] == _set["kind"]

    def test_first_feature(self):
        feature = dashboard[_set["name"]]["chrome"][0]["reports"][0]
        assert feature["path"] == FEATURE_1["path"]
        assert feature["name"] == FEATURE_1["path"]
        assert feature["reportId"] == feature_1_id
        assert feature["parentId"] == set_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_second_feature(self):
        feature = dashboard[_set["name"]]["chrome"][0]["reports"][1]
        assert feature["path"] == FEATURE_2["path"]
        assert feature["name"] == FEATURE_2["path"]
        assert feature["reportId"] == feature_2_id
        assert feature["parentId"] == set_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_first_feature(self):
        feature = dashboard[_set["name"]]["chrome"][0]["reports"][2]
        assert feature["path"] == FEATURE_3["path"]
        assert feature["name"] == FEATURE_3["path"]
        assert feature["reportId"] == feature_3_id
        assert feature["parentId"] == set_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None
