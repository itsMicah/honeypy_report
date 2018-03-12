
class Assertions(object):

    def assert_dates(self, report):
        """
            Verify report dates

            :report: the observed report
        """
        assert report["modified"]
        assert report["created"]

    def assert_scenario(self, observed_scenario, expected_scenario):
        """
            Assert a scenario within a report

            :observed_scenario: the observed report scenario
            :expected_scenario: the expected scenario
        """
        assert observed_scenario["type"] == expected_scenario["type"]
        assert observed_scenario["text"] == expected_scenario["text"]
        assert observed_scenario["name"] == expected_scenario["name"]
        assert observed_scenario["tests"] == expected_scenario["tests"]
        assert observed_scenario["result"] == expected_scenario["result"]
        assert observed_scenario["message"] == expected_scenario["message"]

    def assert_step(self, observed_step, expected_step):
        """
            Assert a step within a report

            :observed_step: the observed step within a report
            :expected_step: the expected step
        """
        assert observed_step["path"] == expected_step["path"]
        assert observed_step["test"] == expected_step["test"]
        assert observed_step["text"] == expected_step["text"]
        assert observed_step["result"] == expected_step["result"]
        assert observed_step["message"] == expected_step["message"]

    def assert_new_report(self, report):
        """
            Assert a new report

            :report: the new report
        """
        self.assert_dates(report)
        assert report["_id"]
        assert report["name"]
        assert report["host"] == "Localhost"
        assert report["url"] == ""
        assert report["browser"] == "chrome"
        assert report["status"] == "Queued"
        assert report["fail"] == False
        assert "message" not in report
        assert report["kind"] in ["feature", "set"]
        if report["kind"] == "feature":
            self.assert_new_feature_report(report)
        elif report["kind"] == "set":
            self.assert_new_set_report(report)
        else:
            assert 0

    def assert_new_feature_report(self, report):
        """
            Assert a new feature report

            :report: the feature report
        """
        assert report["path"]
        assert report["tests"] == []
        assert report["contents"] == []

    def assert_new_set_report(self, report):
        """
            Assert a set report

            :report: the set report
        """
        assert type(report["features"]) == list
        assert type(report["reports"]) == list
        assert report["inherit"] == False

    def assert_queued_feature(self, report, feature_path):
        """
            Assert a queued feature report

            :report: the observed report
            :feature_path: the path of the feature
        """
        assert report["path"] == feature_path
        assert report["result"] == None
        assert report["status"] == "Queued"

    def assert_report_status(self, report, status, result, end = None, message = None):
        """
            Assert the status of a report

            :report: the observed report
            :status: the expected status of a report (queued, running, incomplete)
            :result: the expected boolean value describing the current pass/fail result
            :end: if we expect the report to be done
            :message: the message expected from a report (Success, Failure)
        """
        assert report["status"] == status
        assert report["result"] == result
        if end:
            assert report["end"]
        else:
            assert not end in report
        if message:
            assert report["message"] == message
