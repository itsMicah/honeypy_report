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

    global set_chrome_report, set_chrome_report_id, feature_1_chrome_id, feature_2_chrome_id, feature_3_chrome_id
    global set_firefox_report, set_firefox_report_id, feature_1_firefox_id, feature_2_firefox_id, feature_3_firefox_id
    global set_safari_report, set_safari_report_id, feature_1_safari_id, feature_2_safari_id, feature_3_safari_id
    global set_edge_report, set_edge_report_id, feature_1_edge_id, feature_2_edge_id, feature_3_edge_id
    global set_ie11_report, set_ie11_report_id, feature_1_ie11_id, feature_2_ie11_id, feature_3_ie11_id
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
    set_chrome_report, set_chrome_report_id, feature_1_chrome_id, feature_2_chrome_id, feature_3_chrome_id = init_report("chrome")
    set_firefox_report, set_firefox_report_id, feature_1_firefox_id, feature_2_firefox_id, feature_3_firefox_id = init_report("firefox")
    set_safari_report, set_safari_report_id, feature_1_safari_id, feature_2_safari_id, feature_3_safari_id = init_report("safari")
    set_edge_report, set_edge_report_id, feature_1_edge_id, feature_2_edge_id, feature_3_edge_id = init_report("edge")
    set_ie11_report, set_ie11_report_id, feature_1_ie11_id, feature_2_ie11_id, feature_3_ie11_id = init_report("ie11")

    query = {"environment":SET["environment"]}
    dashboard = helpers.get_dashboard(query)

def init_report(browser):
    _set["browser"] = browser
    id = helpers.create_report(_set)
    report = helpers.get_report(id, True)
    return report, id, report["reports"][0]["_id"], report["reports"][1]["_id"], report["reports"][2]["_id"]


class Test:

    def test_dashboard_response(self):
        """
            Get a dashboard
        """
        assert len(dashboard) == 1
        assert dashboard[_set["name"]]
        assert len(dashboard[_set["name"]]["chrome"]) == 1
        assert len(dashboard[_set["name"]]["firefox"]) == 1
        assert len(dashboard[_set["name"]]["safari"]) == 1
        assert len(dashboard[_set["name"]]["edge"]) == 1
        assert len(dashboard[_set["name"]]["ie11"]) == 1

    def test_dashboard_chrome_results(self):
        set_instance = dashboard[_set["name"]]["chrome"][0]
        assert set_instance["_id"] == _set["name"]
        assert set_instance["browser"] == "chrome"
        assert set_instance["environment"]["name"] == _set["environment"]
        assert set_instance["host"] == _set["host"]
        assert set_instance["kind"] == _set["kind"]

    def test_chrome_first_feature(self):
        feature = dashboard[_set["name"]]["chrome"][0]["reports"][0]
        assert feature["path"] == FEATURE_1["path"]
        assert feature["name"] == FEATURE_1["path"]
        assert feature["reportId"] == feature_1_chrome_id
        assert feature["parentId"] == set_chrome_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_chrome_second_feature(self):
        feature = dashboard[_set["name"]]["chrome"][0]["reports"][1]
        assert feature["path"] == FEATURE_2["path"]
        assert feature["name"] == FEATURE_2["path"]
        assert feature["reportId"] == feature_2_chrome_id
        assert feature["parentId"] == set_chrome_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_chrome_third_feature(self):
        feature = dashboard[_set["name"]]["chrome"][0]["reports"][2]
        assert feature["path"] == FEATURE_3["path"]
        assert feature["name"] == FEATURE_3["path"]
        assert feature["reportId"] == feature_3_chrome_id
        assert feature["parentId"] == set_chrome_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_dashboard_firefox_results(self):
        set_instance = dashboard[_set["name"]]["firefox"][0]
        assert set_instance["_id"] == _set["name"]
        assert set_instance["browser"] == "firefox"
        assert set_instance["environment"]["name"] == _set["environment"]
        assert set_instance["host"] == _set["host"]
        assert set_instance["kind"] == _set["kind"]

    def test_firefox_first_feature(self):
        feature = dashboard[_set["name"]]["firefox"][0]["reports"][0]
        assert feature["path"] == FEATURE_1["path"]
        assert feature["name"] == FEATURE_1["path"]
        assert feature["reportId"] == feature_1_firefox_id
        assert feature["parentId"] == set_firefox_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_firefox_second_feature(self):
        feature = dashboard[_set["name"]]["firefox"][0]["reports"][1]
        assert feature["path"] == FEATURE_2["path"]
        assert feature["name"] == FEATURE_2["path"]
        assert feature["reportId"] == feature_2_firefox_id
        assert feature["parentId"] == set_firefox_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_firefox_third_feature(self):
        feature = dashboard[_set["name"]]["firefox"][0]["reports"][2]
        assert feature["path"] == FEATURE_3["path"]
        assert feature["name"] == FEATURE_3["path"]
        assert feature["reportId"] == feature_3_firefox_id
        assert feature["parentId"] == set_firefox_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_dashboard_safari_results(self):
        set_instance = dashboard[_set["name"]]["safari"][0]
        assert set_instance["_id"] == _set["name"]
        assert set_instance["browser"] == "safari"
        assert set_instance["environment"]["name"] == _set["environment"]
        assert set_instance["host"] == _set["host"]
        assert set_instance["kind"] == _set["kind"]

    def test_safari_first_feature(self):
        feature = dashboard[_set["name"]]["safari"][0]["reports"][0]
        assert feature["path"] == FEATURE_1["path"]
        assert feature["name"] == FEATURE_1["path"]
        assert feature["reportId"] == feature_1_safari_id
        assert feature["parentId"] == set_safari_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_safari_second_feature(self):
        feature = dashboard[_set["name"]]["safari"][0]["reports"][1]
        assert feature["path"] == FEATURE_2["path"]
        assert feature["name"] == FEATURE_2["path"]
        assert feature["reportId"] == feature_2_safari_id
        assert feature["parentId"] == set_safari_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_safari_third_feature(self):
        feature = dashboard[_set["name"]]["safari"][0]["reports"][2]
        assert feature["path"] == FEATURE_3["path"]
        assert feature["name"] == FEATURE_3["path"]
        assert feature["reportId"] == feature_3_safari_id
        assert feature["parentId"] == set_safari_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_dashboard_edge_results(self):
        set_instance = dashboard[_set["name"]]["edge"][0]
        assert set_instance["_id"] == _set["name"]
        assert set_instance["browser"] == "edge"
        assert set_instance["environment"]["name"] == _set["environment"]
        assert set_instance["host"] == _set["host"]
        assert set_instance["kind"] == _set["kind"]

    def test_edge_first_feature(self):
        feature = dashboard[_set["name"]]["edge"][0]["reports"][0]
        assert feature["path"] == FEATURE_1["path"]
        assert feature["name"] == FEATURE_1["path"]
        assert feature["reportId"] == feature_1_edge_id
        assert feature["parentId"] == set_edge_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_edge_second_feature(self):
        feature = dashboard[_set["name"]]["edge"][0]["reports"][1]
        assert feature["path"] == FEATURE_2["path"]
        assert feature["name"] == FEATURE_2["path"]
        assert feature["reportId"] == feature_2_edge_id
        assert feature["parentId"] == set_edge_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_edge_third_feature(self):
        feature = dashboard[_set["name"]]["edge"][0]["reports"][2]
        assert feature["path"] == FEATURE_3["path"]
        assert feature["name"] == FEATURE_3["path"]
        assert feature["reportId"] == feature_3_edge_id
        assert feature["parentId"] == set_edge_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_dashboard_ie11_results(self):
        set_instance = dashboard[_set["name"]]["ie11"][0]
        assert set_instance["_id"] == _set["name"]
        assert set_instance["browser"] == "ie11"
        assert set_instance["environment"]["name"] == _set["environment"]
        assert set_instance["host"] == _set["host"]
        assert set_instance["kind"] == _set["kind"]

    def test_ie11_first_feature(self):
        feature = dashboard[_set["name"]]["ie11"][0]["reports"][0]
        assert feature["path"] == FEATURE_1["path"]
        assert feature["name"] == FEATURE_1["path"]
        assert feature["reportId"] == feature_1_ie11_id
        assert feature["parentId"] == set_ie11_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_ie11_second_feature(self):
        feature = dashboard[_set["name"]]["ie11"][0]["reports"][1]
        assert feature["path"] == FEATURE_2["path"]
        assert feature["name"] == FEATURE_2["path"]
        assert feature["reportId"] == feature_2_ie11_id
        assert feature["parentId"] == set_ie11_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None

    def test_ie11_third_feature(self):
        feature = dashboard[_set["name"]]["ie11"][0]["reports"][2]
        assert feature["path"] == FEATURE_3["path"]
        assert feature["name"] == FEATURE_3["path"]
        assert feature["reportId"] == feature_3_ie11_id
        assert feature["parentId"] == set_ie11_report_id
        assert feature["fail"] == False
        assert feature["status"] == "Queued"
        assert feature["result"] == None
