
class Assertions(object):

    def assert_success(self, test, message = "Success"):
        assert test["result"] == True
        assert test["message"] == message

    def assert_failure(self, test, message = "Failure"):
        assert test["result"] == True
        assert test["message"] == message

    def assert_dates(self, report):
        assert report["modified"]
        assert report["created"]

    def assert_scenario(self, observed_scenario, expected_scenario):
        """
            Assert a scenario object against a scenario inside a report

            :report_scenario: the observed report scenario
            :scenario: the expected scenario
        """
        assert report_scenario["type"] == scenario["type"]
        assert report_scenario["text"] == scenario["text"]
        assert report_scenario["name"] == scenario["name"]
        assert report_scenario["tests"] == scenario["tests"]
        assert report_scenario["result"] == scenario["result"]
        assert report_scenario["message"] == scenario["message"]

    def assert_new_report(self, report):

        self.assert_dates(report)

        assert report["_id"]
        assert report["tests"] == []
        assert report["host"] == "Localhost"
        assert report["url"] == ""
        assert report["browser"] == "chrome"
        assert report["message"] == "Queued"
        assert report["fail"] == False
        assert report["errors"] == []
        assert report["kind"] == report["kind"]
        assert report["path"] == report["path"]
        assert report["contents"] == []
