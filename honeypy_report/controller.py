import time, json, requests
from honeypy.db import DatabaseController as db
from bson.objectid import ObjectId
from bson.errors import InvalidId

class ReportController(object):
    def __init__(self, reportId = None, test = None, config = None):
        self.config = config
        self.db = db("ReportDB", "report_collection", ip = config["DATABASE_URL"], port = config["DATABASE_PORT"])
        self.reportId = reportId
        self.test = test
        self.ifFinish = False

    def response(self, **kwargs):
        if "status" not in kwargs:
            return
        if "data" not in kwargs:
            kwargs["data"] = None
        if "result" not in kwargs:
            if "errors" in kwargs:
                kwargs["result"] = "failure"
            else:
                kwargs["result"] = "success"
        if "errors" not in kwargs:
            kwargs["errors"] = None
        return {
            "result":kwargs["result"],
            "status":kwargs["status"],
            "data":kwargs["data"],
            "errors":kwargs["errors"]
        }

    def createReport(self, data):
        if data["type"] == "test":
            return self.createTestReport(data)
        elif data["type"] == "set":
            return self.createSetReport(data)

    def createTestReport(self, data):
        data["type"] = "test"
        report = {"properties":data, "tests":[]}
        result = self.validateReport(report)
        if result:
            return result
        report = self.setTime(report)
        reportId = self.db.add(report)
        return self.response(data = str(reportId), status = 201)

    def createSetReport(self, data):
        self.setObject = data
        self.setObject["type"] = "set"
        _set = {"properties":self.setObject,"tests":[]}
        for test in data["tests"]:
            index = data["tests"].index(test)
            properties = self.generateTestProperties(test, index)
            _set["tests"].append({"properties":properties, "tests":[]})
        _set = self.setTime(_set)
        reportId = self.db.add(_set)
        return self.response(data = str(reportId), status = 201)

    def generateTestProperties(self, path, index):
        test = {
            "path":path,
            "time":str(round(int(time.time() * 1000))),
            "type":"test",
            "index":index,
            "set":True,
            "id":str(ObjectId())
        }
        response = self.getTestProperties(path)
        data = response["properties"]
        data.update(test)
        if self.setObject["inherit"] == True:
            data.update({
                "url":self.setObject["url"],
                "browser":self.setObject["browser"],
                "host":self.setObject["host"],
                "setName":self.setObject["name"],
            })
        test = data
        return test

    def getTestProperties(self, path):
        response = requests.get(self.config["TEST_URL"] ":" + self.config["TEST_PORT"] + "/tests?path=" + path)
        return response.json()["data"]

    def validateReport(self, report):
        if "type" in report["properties"]:
            if report["properties"]["type"] == "set":
                result = self.validateSetReport(report)
                if result:
                    return result
            else:
                result = self.validateTestReport(report)
                if result:
                    return result
        else:
            return self.response(errors = "Please specify whether this is a test or a set", status = 400)

    def validateTestReport(self, report):
        if "path" not in report["properties"] or not report["properties"]["path"]:
            return self.response(errors = "Please provide a valid test path", status = 400)
        if "name" not in report["properties"] or not report["properties"]["name"]:
            return self.response(errors = "Please provide a valid test name", status = 400)
        if "content" not in report["properties"] or not report["properties"]["content"]:
            return self.response(errors = "Test must contain content", status = 400)
        if "url" not in report["properties"]:
            return self.response(errors = "Please provide a valid URL", status = 400)
        if "browser" not in report["properties"] or not report["properties"]["browser"]:
            return self.response(errors = "Please provider a browser", status = 400)
        if "host" not in report["properties"] or not report["properties"]["host"]:
            return self.response(errors = "Please provide a host", status = 400)

    def validateSetReport(self, report):
        if "tests" not in report["properties"] or not report["properties"]["tests"]:
            return self.response(errors = "Set must contain tests", status = 400)
        if "name" not in report["properties"] or not report["properties"]["name"]:
            return self.response(errors = "Set must have a name", status = 400)
        if "host" not in report["properties"] or not report["properties"]["host"]:
            return self.response(errors = "Please provide a host", status = 400)
        try:
            if report["properties"]["inherit"] == True:
                if "url" not in report["properties"] or not report["properties"]["url"]:
                    return self.response(errors = "Please provide a valid URL", status = 400)
                if "browser" not in report["properties"] or not report["properties"]["browser"]:
                    return self.response(errors = "Please provider a browser", status = 400)
        except KeyError:
            pass

    def setTime(self, report):
        report["properties"]["date"] = time.strftime("%m%d%y")
        report["properties"]["time"] = str(round(int(time.time() * 1000)))
        return report

    def parseObjectIds(self, data):
        if "_id" in data:
            data["_id"] = str(data["_id"])
        if "properties" in data:
            if "_id" in data["properties"]:
                data["properties"]["_id"] = str(data["properties"]["_id"])
            if "type" in data["properties"]:
                if data["properties"]["type"] == "set":
                    for test in data["tests"]:
                        index = data["tests"].index(test)
                        if data["tests"][index]["properties"]:
                            if "id" in data["tests"][index]["properties"]:
                                data["tests"][index]["properties"]["id"] = str(data["tests"][index]["properties"]["id"])
        return data

    def getReport(self):
        try:
            report = self.db.getData({"_id":ObjectId(self.reportId)}, False)
            if not report:
                return self.response(errors = "Unable to find report", status = 404)
            report = self.cleanObjectId(report)
            return self.response(data = report, status = 200)
        except InvalidId:
            return self.response(errors = "Unable to find report", status = 404)

    def getReportsByDate(self, search):
        result = self.validateSearchByDate(search)
        if result:
            return result
        results = None
        if search["type"] == "set":
            results = self.db.getData({"properties.type":"set", "properties.name":search["set"], "properties.time": {"$lte":search["max"], "$gte":search["min"]} })
        else:
            results = self.db.getData({"properties.time": {"$lte":search["max"], "$gte":search["min"]} })
        results = self.cleanseCursorObject(results)
        return self.response(data = results, status = 200)

    def searchSetReports(self, search):
        results = self.db.getData({"properties.time": {"$lte":search["max"], "$gte":search["min"]} })

    def validateSearchByDate(self, search):
        if "min" not in search or not search["min"]:
            return self.response(errors = "Please provide a minimum timestamp", status = 400)
        if "max" not in search or not search["max"]:
            return self.response(errors = "Please provide a maximium timestamp", status = 400)
        if "type" not in search or not search["type"]:
            return self.response(errors = "Please a search type", status = 400)

    def cleanseCursorObject(self, data):
        node = []
        for item in data:
            item = self.cleanObjectId(item)
            node.append(item)
        return node

    def cleanObjectId(self, node):
        if "_id" in node:
            node["_id"] = str(node["_id"])
        return node

    def patchReport(self, data):
        _filter = {"_id":ObjectId(self.reportId)}
        data = self.db.patch(data, _filter)
        return data

    def extendArray(self, data):
        _filter = {"_id":ObjectId(self.reportId)}
        data = self.db.extendArray(data, _filter)
        if data["_id"]:
            data["_id"] = str(data["_id"])
        return data

    def putReport(self, data):
        data = self.db.edit(data, {"_id":ObjectId(self.reportId)})
        return data

    def deleteReport(self):
        try:
            result = self.checkReport()
            if result:
                return result
            self.db.delete({"_id":ObjectId(self.reportId)})
            return self.response(status = 204)
        except InvalidId:
            return self.response(errors = "Unable to find report", status = 404)

    def validateAddReport(self, data):
        if "test" not in data or not data["test"]:
            return self.response(errors = "Please provide a test to add to the report", status = 400)
        if not "type" in data["properties"] or not data["properties"]["type"]:
            data["properties"]["type"] = "test"
        if data["properties"]["set"]:
            if "index" not in data["properties"]:
                return self.response(errors = "Please provide an index", status = 400)
        return self.checkReport()

    def addReport(self, data):
        result = self.validateAddReport(data)
        if result:
            return result
        test = data["test"]
        _type = self.ifTestinSet(data)
        index = data["properties"]["index"]
        if _type:
            self.addTestToSet(test, index)
        else:
            self.addTest(test)
        return self.response(status = 201)

    def ifTestinSet(self, data):
        if "set" in  data["properties"]:
            return data["properties"]["set"]
        else:
            return False

    def checkReport(self):
        report = self.db.getData({"_id":ObjectId(self.reportId)}, False)
        if not report:
            return self.response(errors = "Unable to find report", status = 404)

    def addTestToSet(self, test, index):
            if "scenarioId" in test:
                if test["scenarioId"]:
                    report = self.getReport()
                    for line in report["tests"][index]["tests"]:
                        if line["type"] == "scenario":
                            if line["id"] == test["scenarioId"]:
                                lineIndex = report["tests"][index]["tests"].index(line)
                                self.extendArray({"tests." + str(index) + ".tests." + str(lineIndex) + ".tests":test})
                else:
                    self.extendArray({"tests." + str(index) + ".tests":test})
            else:
                self.extendArray({"tests." + str(index) + ".tests":test})

    def addTest(self, test):
            try:
                if test["scenarioId"]:
                    report = self.db.getData({"_id":ObjectId(self.reportId)}, False)
                    report = self.cleanObjectId(report)
                    for line in report["tests"]:
                        if line["type"] == "scenario":
                            if line["id"] == test["scenarioId"]:
                                lineIndex = report["tests"].index(line)
                                self.extendArray({"tests." + str(lineIndex) + ".tests":test})
                else:
                    self.extendArray({"tests":test})
            except KeyError:
                self.extendArray({"tests":test})

    def finished(self):
        report = self.db.getData({"_id":ObjectId(self.reportId)}, False)
        if report["properties"]["type"] == "set":
            return self.finishSet(report)
        else:
            return self.checkTestStatus(report)

    def finishSet(self, report):
        report["_id"] = ObjectId(report["_id"])
        report["properties"]["_id"] = ObjectId(report["properties"]["_id"])
        return self.checkSetStatus(report)

    def checkIfSetFinished(self, report = None):
        if report == None:
             report = self.getReport()["data"]
        self.ifFinish = True
        for test in report["tests"]:
            if "end" not in test["properties"]:
                self.ifFinish = False
        if self.ifFinish == True:
            currentTime = str(round(int(time.time() * 1000)))
            self.patchReport({"properties.end":currentTime})

    def checkSetStatus(self, report):
        totalResult = True
        totalMessage = "Success"
        for test in report["tests"]:
            index = report["tests"].index(test)
            self.checkTestStatus(test, index)
            if test["properties"]["result"] == False:
                totalResult = False
                totalMessage = "Failure"
            report["tests"][index] = test
        self.patchReport({"properties.result":totalResult})
        self.patchReport({"properties.message":totalMessage})
        return self.response(status = 204)

    def checkTestStatus(self, test, testIndex = None):
        totalResult = True
        totalMessage = "Success"
        for subTest in test["tests"]:
            index = test["tests"].index(subTest)
            subTest = self.checkScenarioStatus(subTest, index, testIndex)
            # CHECK IF JS
            if "result" in subTest:
                if subTest["result"] == False:
                    totalResult = False
                    totalMessage = "Failure"
            test["tests"][index] = subTest
        if testIndex != None:
            self.patchReport({"tests." + str(testIndex) + ".properties.result":totalResult})
            self.patchReport({"tests." + str(testIndex) + ".properties.message":totalMessage})
        else:
            self.patchReport({"properties.result":totalResult})
            self.patchReport({"properties.message":totalMessage})
        test["properties"]["result"] = totalResult
        test["properties"]["message"] = totalMessage
        if self.test == test["properties"]["path"]:
            self.endTest(testIndex)
        elif test["properties"]["type"] == "test":
            self.endTest()
        return self.response(status = 204)

    def checkScenarioStatus(self, subTest, subTestIndex, testIndex = None):
        if subTest["type"] == "scenario":
            totalResult = True
            totalMessage = "Success"
            scenarioTestIndex = None
            for test in subTest["tests"]:
                scenarioTestIndex = subTest["tests"].index(test)
                try:
                    if test["result"] == False:
                        totalResult = False
                        totalMessage = "Failure"
                except:
                    pass
            if scenarioTestIndex != None and testIndex != None:
                self.patchReport({"tests." + str(testIndex) + ".tests." + str(subTestIndex) + ".result":totalResult})
                self.patchReport({"tests." + str(testIndex) + ".tests." + str(subTestIndex) + ".message":totalMessage})
            if testIndex == None:
                self.patchReport({"tests." + str(subTestIndex) + ".result":totalResult})
                self.patchReport({"tests." + str(subTestIndex) + ".message":totalMessage})
            subTest["result"] = totalResult
            subTest["message"] = totalMessage
        return subTest

    def endTest(self, index = None):
        if index != None:
            response = self.patchReport({"tests." + str(index) + ".properties.end":str(round(int(time.time() * 1000)))})
            self.checkIfSetFinished()
        else:
            response = self.patchReport({"properties.end":str(round(int(time.time() * 1000)))})
