import pytest, requests, time

testReport = {
    "path":"/path/to/a/folder/test.api",
    "name":"test.api",
    "host": "Localhost",
    "browser":"Chrome",
    "url":"http://www.google.com/",
    "content": [
        "# TEST CONTENT",
        "  Given I am on the /images page",
        "    Then the page should contain the text 'images'"
    ],
    "type":"test"
}
invalidReportId = "FAKEIDRIGHTHEYA"

def create(report):
    return requests.post("http://localhost:8001/report", json=report)

def get(reportId):
    return requests.get("http://localhost:8001/report/" + reportId)

def delete(reportId):
    return requests.delete("http://localhost:8001/report/" + reportId)

def search(min, max):
    return requests.post("http://localhost:8001/report/search", json={"min":min, "max":max})

def add(reportId, data):
    return requests.patch("http://localhost:8001/report/" + reportId + "/add", json=data)

def finish(reportId):
    return requests.get("http://localhost:8001/report/" + reportId + "/finish")

# TESTS

@pytest.mark.parametrize("report, message", [
    ({}, "Please specify whether this is a test or a set"),
    ({"type":"test"}, "Please provide a valid test path"),
    ({"type":"test", "path":"/fake/path.api"}, "Please provide a valid test name"),
    ({"type":"test", "path":"/fake/path.api", "name":"path.api"}, "Test must contain content"),
    ({"type":"test", "path":"/fake/path.api", "name":"path.api", "content":["hello"]}, "Please provide a valid URL"),
    ({"type":"test", "path":"/fake/path.api", "name":"path.api", "content":["hello"], "url":"http://www.google.com"}, "Please provider a browser"),
    ({"type":"test", "path":"/fake/path.api", "name":"path.api", "content":["hello"], "url":"http://www.google.com", "browser":"Chrome"}, "Please provide a host")
])
def test_invalid_test_report_creation(report, message):
    response = create(report)
    assert response.status_code == 400
    json = response.json()
    assert not json["data"]
    assert json["result"] == "failure"
    assert json["errors"] == message

@pytest.mark.parametrize("report, message", [
    ({}, "Please specify whether this is a test or a set"),
    ({"type":"set"}, "Set must contain tests"),
    ({"type":"set", "tests":["/test/fake.path"]}, "Set must have a name"),
    ({"type":"set", "tests":["/test/fake.path"], "name":"FAKE NAME"}, "Please provide a host"),
    ({"type":"set", "inherit": True, "tests":["/test/fake.path"], "name":"FAKE NAME", "host":{"ip":"0.0.0.0"}}, "Please provide a valid URL"),
    ({"type":"set", "inherit": True, "tests":["/test/fake.path"], "name":"FAKE NAME", "host":{"ip":"0.0.0.0"}, "url":"http://www.google.com"}, "Please provider a browser"),
])
def test_invalid_set_report_creation(report, message):
    response = create(report)
    assert response.status_code == 400
    json = response.json()
    assert not json["data"]
    assert json["result"] == "failure"
    assert json["errors"] == message

def test_test_report_create():
    response = create(testReport)
    json = response.json()
    assert response.status_code == 201
    assert not json["errors"]
    assert json["result"] == "success"
    assert len(json["data"]) > 0
    reportId = json["data"]

    response = get(reportId)
    assert response.status_code == 200
    json = response.json()
    assert not json["errors"]
    assert json["result"] == "success"
    json["data"].pop("_id", None)
    assert json["data"]["properties"]["path"] == testReport["path"]
    assert json["data"]["properties"]["name"] == testReport["name"]
    assert json["data"]["properties"]["host"] == testReport["host"]
    assert json["data"]["properties"]["browser"] == testReport["browser"]
    assert json["data"]["properties"]["url"] == testReport["url"]
    assert json["data"]["properties"]["content"] == testReport["content"]
    assert json["data"]["properties"]["type"] == testReport["type"]
    assert json["data"]["properties"]["date"]
    assert json["data"]["properties"]["time"]
    assert json["data"]["tests"] == []

    response = delete(reportId)
    assert response.status_code == 204

    response = get(reportId)
    assert response.status_code == 404

def test_get_invalid_report_id():
    response = get(invalidReportId)
    assert response.status_code == 404
    json = response.json()
    assert not json["data"]
    assert json["result"] == "failure"
    assert json["errors"] == "Unable to find report"

def test_delete_invalid_report_id():
    response = delete(invalidReportId)
    assert response.status_code == 404
    json = response.json()
    assert not json["data"]
    assert json["result"] == "failure"
    assert json["errors"] == "Unable to find report"

def test_add_line_to_test_report():
    response = create(testReport)
    assert response.status_code == 201
    reportId = response.json()["data"]

    response = get(reportId)
    assert response.status_code == 200
    json = response.json()
    assert len(json["data"]["tests"]) == 0
    assert json["data"]["_id"] == reportId

    testA = {
        "test":{"type":"test","test":"Given I am on the page"},
        "properties": {
            "set":False,
            "index":None
        }
    }

    response = add(reportId, testA)
    assert response.status_code == 201
    response = get(reportId)
    assert response.status_code == 200
    json = response.json()
    assert not json["errors"]
    assert json["result"] == "success"
    assert len(json["data"]["tests"]) == 1
    assert json["data"]["tests"][0] == testA["test"]

    testB = {
        "test":{"type":"test","test":"Given I am on the second page"},
        "properties": {
            "set":False,
            "index":None
        }
    }

    response = add(reportId, testB)
    assert response.status_code == 201
    response = get(reportId)
    assert response.status_code == 200
    json = response.json()
    assert not json["errors"]
    assert json["result"] == "success"
    assert len(json["data"]["tests"]) == 2
    assert json["data"]["tests"][1] == testB["test"]

    testC = {
        "test":{"type":"scenario","name":"Test Scenario", "id":"Verify testing", "tests":[]},
        "properties": {
            "set":False,
            "index":None
        }
    }

    response = add(reportId, testC)
    assert response.status_code == 201
    response = get(reportId)
    assert response.status_code == 200
    json = response.json()
    assert not json["errors"]
    assert json["result"] == "success"
    assert len(json["data"]["tests"]) == 3
    assert json["data"]["tests"][2] == testC["test"]

    testD = {
        "test":{"type":"http","name":"Test Scenario", "scenarioId":"Verify testing", "test":"HERE I AM TO WORSHIP AND BOW DOWN"},
        "properties": {
            "set":False,
            "index":None
        }
    }

    response = add(reportId, testD)
    assert response.status_code == 201
    response = get(reportId)
    assert response.status_code == 200
    json = response.json()
    assert not json["errors"]
    assert json["result"] == "success"
    assert len(json["data"]["tests"]) == 3
    assert len(json["data"]["tests"][2]["tests"]) == 1
    assert json["data"]["tests"][2]["tests"][0] == testD["test"]

    response = add(reportId, testD)
    assert response.status_code == 201
    response = get(reportId)
    assert response.status_code == 200
    json = response.json()
    assert not json["errors"]
    assert json["result"] == "success"
    assert len(json["data"]["tests"]) == 3
    assert len(json["data"]["tests"][2]["tests"]) == 2
    assert json["data"]["tests"][2]["tests"][1] == testD["test"]

    testE = {
        "test":{"type":"scenario","name":"Second Test Scenario", "id":"Verify testing times 2", "tests":[]},
        "properties": {
            "set":False,
            "index":None
        }
    }

    response = add(reportId, testE)
    assert response.status_code == 201
    response = get(reportId)
    assert response.status_code == 200
    json = response.json()
    assert not json["errors"]
    assert json["result"] == "success"
    assert len(json["data"]["tests"]) == 4
    assert json["data"]["tests"][3] == testE["test"]

    testF = {
        "test":{"type":"http","name":"Test Scenario", "scenarioId":"Verify testing times 2", "test":"HERE I AM TO WORSHIP AND BOW DOWN"},
        "properties": {
            "set":False,
            "index":None
        }
    }

    response = add(reportId, testF)
    assert response.status_code == 201
    response = get(reportId)
    assert response.status_code == 200
    json = response.json()
    assert not json["errors"]
    assert json["result"] == "success"
    assert len(json["data"]["tests"]) == 4
    assert len(json["data"]["tests"][3]["tests"]) == 1
    assert json["data"]["tests"][3]["tests"][0] == testF["test"]

    response = delete(reportId)
    assert response.status_code == 204

def test_finish_test_report():
    response = create(testReport)
    assert response.status_code == 201
    reportId = response.json()["data"]

    response = get(reportId)
    assert response.status_code == 200
    json = response.json()
    assert len(json["data"]["tests"]) == 0
    assert json["data"]["_id"] == reportId
    response = finish(reportId)
    assert response.status_code == 204
    response = get(reportId)
    assert response.status_code == 200
    json = response.json()
    assert not json["errors"]
    assert json["result"] == "success"
    assert json["data"]["properties"]["result"] == True
    assert json["data"]["properties"]["message"] == "Success"

    response = delete(reportId)
    assert response.status_code == 204

    response = get(reportId)
    assert response.status_code == 404
