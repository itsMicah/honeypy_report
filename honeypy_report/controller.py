import time, json, pymongo, re, datetime
from pymongo import MongoClient
from flask import Flask
from honeypy.api.test import TestService
from bson.objectid import ObjectId
from bson.errors import InvalidId
from mongoengine import *
from honeypy.errors import CustomFileNotFound

from honeypy_report import report_api
from honeypy.api.common import Common
from honeypy_report.models import FeatureReport, SetReport, Report, Test, Scenario, Step

class ReportController(object):

    def __init__(self):
        self.config = report_api.config
        self.common = Common()
        self.ifFinish = False
        self.initiate_db()

    def initiate_db(self):
        """
            Start database session
        """
        uri = 'mongodb://' + self.config['DATABASE_IP'] + ':' + str(self.config['DATABASE_PORT'])
        client = MongoClient(uri)
        db = client[self.config['REPORT_DB']]
        self.collection = db[self.config['REPORT_DB']]

    def check_kind(self, data):
        """
            Check if kind field is present in payload
        """
        if not "kind" in data or not data["kind"]:
            raise ValidationError(errors = {"kind": "Please provide a valid 'kind' ['set', 'feature']"})

    def get(self, report_id):
        """
            Get a report by ID and kind

            :kind: the type of report
            :report_id: the id of the requested report
        """
        response = Report.objects(id=report_id).get().to_json()
        return self.common.create_response(200, response)

    def create(self, data):
        """
            Create a feature/set report

            :data: the request payload
        """
        self.check_kind(data)
        data = self.common.clean(data)
        report = None
        if data["kind"] == "feature":
            report = self.create_feature_report(data)
        elif data["kind"] == "set":
            report = self.create_set_report(data)
        return self.common.create_response(201, json.dumps({"id":str(report.id)}))

    def create_feature_report(self, data):
        response = TestService().get(data["path"], "feature")
        if response.status_code == 200:
            data["reportId"] = None
            report = FeatureReport(**data)
            report.save(force_insert=True)
            return report
        elif response.status_code == 404:
            raise CustomFileNotFound()

    def create_set_report(self, data):
        """
            Create a set report
        """
        response = SetService().get(data["name"])
        _set = response.json()
        _set["tests"] = []
        _set["errors"] = []
        report = SetReport(**_set).save()
        self.append_set_tests(report, _set)
        return report

    def append_set_tests(self, report, data):
        """
            Populate set report with sub feature reports

            :report: the report object
            :data: the data to push to the report object
        """
        for path in data["features"]:
            response = TestService().get(path, "feature")
            if response.status_code == 404:
                SetReport.objects(id = report.id).update_one(push__errors=f"'{path}' does not exist")
                SetReport.objects(id = report.id).update_one(pull__features=path)
            elif response.status_code == 200:
                feature = response.json()
                feature = self.common.clean(feature)
                feature["tests"] = []
                feature["result"] = None
                feature["reportId"] = report.id
                feature["message"] = "Incomplete"
                SetReport.objects(id = report.id).update_one(push__tests=feature)

    def save(self, report_id, data):
        """
            Save to a report
        """
        self.check_kind(data)
        data = self.common.pre_save_document(data)
        Report.objects(id = report_id).modify(set__modified = datetime.datetime.now)
        Report.objects(id = report_id).update_one(**data)
        return self.common.create_response(204)

    def add(self, report_id, data):
        """
            Add to report
        """
        self.verify_add(data)
        kind = data["kind"]
        data.pop("kind", None)
        if data["result"] == False:
            Report.objects(id = report_id).update_one(set__result = data["result"], set__message = "Failure")
        if "scenarioId" in data:
            if type(data["scenarioId"]) != str:
                data["scenarioId"] = ObjectId(data["scenarioId"])
        Report.objects(id = report_id).modify(set__modified = datetime.datetime.now)
        if kind == "feature":
            self.add_to_feature(report_id, data)
        elif kind == "set":
            self.add_to_set(report_id, data)
        return self.common.create_response(204)

    def verify_add(self, data):
        if not "kind" in data or not data["kind"] or not re.match(r"(feature|set)", data["kind"]):
            raise ValidationError(errors = {"kind": "Please provide a valid 'kind' ['set', 'feature']"})
        if not "_type" in data or not data["_type"] or not re.match(r"(scenario|test)", data["_type"]):
            raise ValidationError(errors = {"_type": "Please provide a valid '_type' ['test', 'scenario']"})

    def add_to_feature(self, report_id, data):
        data.pop("path", None)
        if data["_type"] == "test" and not "scenarioId" in data:
            FeatureReport.objects(id = report_id).modify(push__tests=Step(**data))
        elif data["_type"] == "scenario" and "scenarioId" in data:
            FeatureReport.objects(id = report_id).modify(push__tests=Scenario(**data))
        elif data["_type"] == "test" and data["scenarioId"]:
            print("ADD")
            print(data)
            if data["result"] == False:
                print("FALSE")
                self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"scenarioId": ObjectId(data["scenarioId"])}}}, {'$set': {'tests.$.result':data["result"], 'tests.$.message':"Failure"}})
            self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"scenarioId": ObjectId(data["scenarioId"])}}}, {'$push': {'tests.$.tests':data}})

    def add_to_set(self, report_id, data):
        self.verify_set_add(data)
        if data["_type"] == "test" and not "scenarioId" in data:
            result = self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"path": data["path"]}} }, {'$push': {'tests.$.tests':data}})
        elif data["_type"] == "scenario" and "scenarioId" in data:
            result = self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"path": data["path"]}} }, {'$push': {'tests.$.tests':data}})
            if data["result"] == False:
                result = self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"scenarioId": ObjectId(data["scenarioId"])}}}, {'$set': {'tests.$.result':data["result"]}, '$set': {'tests.$.message':data["message"]}})
        elif data["_type"] == "test" and data["scenarioId"]:
            if data["result"] == False:
                result = self.collection.update_one({ "_id": ObjectId(report_id) }, {'$set': {'tests.$[a].tests.$[b].message':data["message"], 'tests.$[a].tests.$[b].result':data["result"]}}, array_filters=[{"a.path":data["path"]}, {"b.scenarioId":data["scenarioId"]}])
                result = self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"path": data["path"]}}}, {'$set': {'tests.$.result':data["result"], 'tests.$.message':data["message"]}})
            result = self.collection.update_one({ "_id": ObjectId(report_id) }, {'$push': {'tests.$[a].tests.$[b].tests':data}}, array_filters=[{"a.path":data["path"]}, {"b.scenarioId":data["scenarioId"]}])
            if result.acknoledge == False:
                raise OperationFailure({"Scenario not found"})


    def verify_set_add(self, data):
        if not "path" in data or not data["path"]:
            raise ValidationError(errors = {"path": "Please provide a valid path to add append a report"})

    def finish(self, report_id, path, result = True, message = "Success"):
        report = json.loads(Report.objects(id=report_id).get().to_json())
        if report["kind"] == "feature":
            result, message = self.finish_feature_report(report, result, message)
            self.final_finish(report_id, result, message)
        elif report["kind"] == "set":
            if path:
                if not path in report["features"]:
                    raise ValidationError(errors = {"path":"Path does not exist in the set"})
                for test in report["tests"]:
                    if test["path"] == path:
                        result, message = self.finish_feature_report(test, result, message)
                        self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"path": path}} }, {'$set': {'tests.$.tests.result':result,'tests.$.tests.message':message, 'tests.$.tests.end':str(datetime.datetime.now)}}, upsert = True)
                        break
            else:
                for feature in report["tests"]:
                    result, message = self.finish_feature_report(feature, result, message)
                    self.final_finish(report_id, result, message)
        return self.common.create_response(204)

    def finish_feature_report(self, report, result, message):
        for test in report["tests"]:
            if not "result" in test or test["result"] == False:
                result = False
                message = "Failure"
                break
        return result, message

    def final_finish(self, report_id, result, message):
        Report.objects(id = report_id).modify(set__end = datetime.datetime.now, set__modified = datetime.datetime.now, set__result = result, set__message = message)



            # if not "scenarioId" in data and "kind" in data:
            #     SetReport.objects(_id = report_id).modify(push__tests=data)
            # elif not "scenarioId" in data and not "kind" in data:
            #
            # else:
            #     SetReport.objects(_id = report_id, Scenario__scenarioId).modify(push__scenario__tests=data)
            # Set.objects(name=name).modify(push__set__features=data)

    # def getReportsByDate(self, search):
    #     result = self.validateSearchByDate(search)
    #     if result:
    #         return result
    #     results = None
    #     if search["kind"] == "set":
    #         results = self.db.get_data({"properties.type":"set", "properties.name":search["set"], "properties.time": {"$lte":search["max"], "$gte":search["min"]} })
    #     else:
    #         results = self.db.get_data({"properties.time": {"$lte":search["max"], "$gte":search["min"]} })
    #     results = self.cleanseCursorObject(results)
    #     return self.response(data = results, status = 200)
    #
    # def searchSetReports(self, search):
    #     results = self.db.get_data({"properties.time": {"$lte":search["max"], "$gte":search["min"]} })
    #
    # def validateSearchByDate(self, search):
    #     if "min" not in search or not search["min"]:
    #         return self.response(errors = "Please provide a minimum timestamp", status = 400)
    #     if "max" not in search or not search["max"]:
    #         return self.response(errors = "Please provide a maximium timestamp", status = 400)
    #     if "kind" not in search or not search["kind"]:
    #         return self.response(errors = "Please a search type", status = 400)
    #
    # def cleanseCursorObject(self, data):
    #     node = []
    #     for item in data:
    #         item = self.cleanObjectId(item)
    #         node.append(item)
    #     return node
    #
    # def cleanObjectId(self, node):
    #     if "_id" in node:
    #         node["_id"] = str(node["_id"])
    #     return node
    #
    # def patchReport(self, data):
    #     _filter = {"_id":ObjectId(self.reportId)}
    #     data = self.db.patch(data, _filter)
    #     return data
    #
    # def extend_array(self, data):
    #     _filter = {"_id":ObjectId(self.reportId)}
    #     data = self.db.extend_array(data, _filter)
    #     if data["_id"]:
    #         data["_id"] = str(data["_id"])
    #     return data
    #
    # def putReport(self, data):
    #     data = self.db.edit(data, {"_id":ObjectId(self.reportId)})
    #     return data
    #
    # def deleteReport(self):
    #     try:
    #         result = self.checkReport()
    #         if result:
    #             return result
    #         self.db.delete({"_id":ObjectId(self.reportId)})
    #         return self.response(status = 204)
    #     except InvalidId:
    #         return self.response(errors = "Unable to find report", status = 404)
    #
    # def validateAddReport(self, data):
    #     if "test" not in data or not data["test"]:
    #         return self.response(errors = "Please provide a test to add to the report", status = 400)
    #     if not "kind" in data["properties"] or not data["properties"]["kind"]:
    #         data["properties"]["kind"] = "feature"
    #     if data["properties"]["set"]:
    #         if "index" not in data["properties"]:
    #             return self.response(errors = "Please provide an index", status = 400)
    #     return self.checkReport()
    #
    # def addReport(self, data):
    #     result = self.validateAddReport(data)
    #     if result:
    #         return result
    #     test = data["test"]
    #     _type = self.ifTestinSet(data)
    #     index = data["properties"]["index"]
    #     if _type:
    #         self.addTestToSet(test, index)
    #     else:
    #         self.addTest(test)
    #     return self.response(status = 201)
    #
    # def ifTestinSet(self, data):
    #     if "set" in  data["properties"]:
    #         return data["properties"]["set"]
    #     else:
    #         return False
    #
    # def checkReport(self):
    #     report = self.db.get_data({"_id":ObjectId(self.reportId)}, False)
    #     if not report:
    #         return self.response(errors = "Unable to find report", status = 404)
    #
    # def addTestToSet(self, test, index):
    #         if "scenarioId" in test:
    #             if test["scenarioId"]:
    #                 report = self.getReport()
    #                 for line in report["tests"][index]["tests"]:
    #                     if line["kind"] == "scenario":
    #                         if line["id"] == test["scenarioId"]:
    #                             lineIndex = report["tests"][index]["tests"].index(line)
    #                             self.extend_array({"tests." + str(index) + ".tests." + str(lineIndex) + ".tests":test})
    #             else:
    #                 self.extend_array({"tests." + str(index) + ".tests":test})
    #         else:
    #             self.extend_array({"tests." + str(index) + ".tests":test})
    #
    # def addTest(self, test):
    #         try:
    #             if test["scenarioId"]:
    #                 report = self.db.get_data({"_id":ObjectId(self.reportId)}, False)
    #                 report = self.cleanObjectId(report)
    #                 for line in report["tests"]:
    #                     if line["kind"] == "scenario":
    #                         if line["id"] == test["scenarioId"]:
    #                             lineIndex = report["tests"].index(line)
    #                             self.extend_array({"tests." + str(lineIndex) + ".tests":test})
    #             else:
    #                 self.extend_array({"tests":test})
    #         except KeyError:
    #             self.extend_array({"tests":test})
    #
    # def finished(self):
    #     report = self.db.get_data({"_id":ObjectId(self.reportId)}, False)
    #     if report["properties"]["kind"] == "set":
    #         return self.finishSet(report)
    #     else:
    #         return self.checkTestStatus(report)
    #
    # def finishSet(self, report):
    #     report["_id"] = ObjectId(report["_id"])
    #     report["properties"]["_id"] = ObjectId(report["properties"]["_id"])
    #     return self.checkSetStatus(report)
    #
    # def checkIfSetFinished(self, report = None):
    #     if report == None:
    #          report = self.getReport()["data"]
    #     self.ifFinish = True
    #     for test in report["tests"]:
    #         if "end" not in test["properties"]:
    #             self.ifFinish = False
    #     if self.ifFinish == True:
    #         currentTime = str(round(int(time.time() * 1000)))
    #         self.patchReport({"properties.end":currentTime})
    #
    # def checkSetStatus(self, report):
    #     totalResult = True
    #     totalMessage = "Success"
    #     for test in report["tests"]:
    #         index = report["tests"].index(test)
    #         self.checkTestStatus(test, index)
    #         if "end" in test["properties"]:
    #             if test["properties"]["result"] == False:
    #                 totalResult = False
    #                 totalMessage = "Failure"
    #             report["tests"][index] = test
    #     self.patchReport({"properties.result":totalResult})
    #     self.patchReport({"properties.message":totalMessage})
    #     return self.response(status = 204)
    #
    # def checkTestStatus(self, test, testIndex = None):
    #     totalResult = True
    #     totalMessage = "Success"
    #     for subTest in test["tests"]:
    #         index = test["tests"].index(subTest)
    #         subTest = self.checkScenarioStatus(subTest, index, testIndex)
    #         # CHECK IF JS
    #         if "result" in subTest:
    #             if subTest["result"] == False:
    #                 totalResult = False
    #                 totalMessage = "Failure"
    #         test["tests"][index] = subTest
    #     if testIndex != None:
    #         self.patchReport({"tests." + str(testIndex) + ".properties.result":totalResult})
    #         self.patchReport({"tests." + str(testIndex) + ".properties.message":totalMessage})
    #     else:
    #         self.patchReport({"properties.result":totalResult})
    #         self.patchReport({"properties.message":totalMessage})
    #     test["properties"]["result"] = totalResult
    #     test["properties"]["message"] = totalMessage
    #     if self.path == test["properties"]["path"] and testIndex != None:
    #         self.endTest(testIndex)
    #     elif self.getReport()["data"]["properties"]["kind"] == "feature":
    #         self.endTest()
    #     return self.response(status = 204)
    #
    # def checkScenarioStatus(self, subTest, subTestIndex, testIndex = None):
    #     if subTest["type"] == "scenario":
    #         totalResult = True
    #         totalMessage = "Success"
    #         scenarioTestIndex = None
    #         for test in subTest["tests"]:
    #             scenarioTestIndex = subTest["tests"].index(test)
    #             try:
    #                 if test["result"] == False:
    #                     totalResult = False
    #                     totalMessage = "Failure"
    #             except:
    #                 pass
    #         if scenarioTestIndex != None and testIndex != None:
    #             self.patchReport({"tests." + str(testIndex) + ".tests." + str(subTestIndex) + ".result":totalResult})
    #             self.patchReport({"tests." + str(testIndex) + ".tests." + str(subTestIndex) + ".message":totalMessage})
    #         if testIndex == None:
    #             self.patchReport({"tests." + str(subTestIndex) + ".result":totalResult})
    #             self.patchReport({"tests." + str(subTestIndex) + ".message":totalMessage})
    #         subTest["result"] = totalResult
    #         subTest["message"] = totalMessage
    #     return subTest
    #
    # def endTest(self, index = None):
    #     if index != None:
    #         response = self.patchReport({"tests." + str(index) + ".properties.end":str(round(int(time.time() * 1000)))})
    #         self.checkIfSetFinished()
    #     else:
    #         response = self.patchReport({"properties.end":str(round(int(time.time() * 1000)))})
