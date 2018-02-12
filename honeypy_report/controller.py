import time, json, pymongo, re, datetime
from cerberus import Validator
from pymongo import MongoClient
from flask import Flask
from honeypy.api.test import TestService
from honeypy.api.set import SetService
from bson.objectid import ObjectId
from bson.errors import InvalidId
from mongoengine import *
from honeypy.errors import CustomFileNotFound, ValidationError

from honeypy_report.schema import Schemas
from honeypy_report import report_api
from honeypy.api.common import Common, Database
from honeypy_report.models import FeatureReport, SetReport, Report, Test, Scenario, Step

class ReportController(object):

    def __init__(self):
        self.config = report_api.config
        self.common = Common()
        self.ifFinish = False
        self.db = Database(report_api.config['DATABASE_IP'], report_api.config['DATABASE_PORT'], report_api.config['REPORT_DB'])

    def get(self, report_id):
        """
            Get a report by ID and kind

            :kind: the type of report
            :report_id: the id of the requested report
        """
        document = self.db.find_one({"_id":ObjectId(report_id)})
        return self.common.create_response(200, document)

    def create(self, data):
        data = self.validate_report(data)
        response = self.db.insert_one(data)
        return self.common.create_response(201, {"id":str(response.inserted_id)})

    def validate_report(self, data, update = False, normalize = True):
        """
            Create a feature/set report

            :data: the request payload
        """
        validator = Validator(Schemas().report)
        validation = validator.validate(data, update = update, normalize = normalize)
        if not validation:
            raise ValidationError(validator.errors)
        return self.validate_report_type(data, update, normalize)

    def validate_report_type(self, data, update, normalize):
        validator = Validator({}, purge_unknown = True)
        validation = None
        schemas = Schemas()
        if data["kind"] == "set":
            validator.schema = schemas.set_report
        elif data["kind"] == "feature":
            validator.schema = schemas.feature_report
        validation = validator.validate(data, update = update, normalize = normalize)
        if not validation:
            raise ValidationError(validator.errors)
        return data

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
                feature["setId"] = report.id
                feature["message"] = "Incomplete"
                if data["inherit"] == True:
                    feature["browser"] = data["browser"]
                    feature["url"] = data["url"]
                    feature["host"] = data["host"]
                SetReport.objects(id = report.id).update_one(push__tests=feature)

    def save(self, report_id, data):
        """
            Save to a report
        """
        data = self.validate_report(data, True, False)
        self.db.update_one({"_id":ObjectId(report_id)}, data)
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
            if data["result"] == False:
                self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"scenarioId": ObjectId(data["scenarioId"])}}}, {'$set': {'tests.$.result':data["result"], 'tests.$.message':"Failure", 'result':data["result"], 'message':"Failure"}})
            self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"scenarioId": ObjectId(data["scenarioId"])}}}, {'$push': {'tests.$.tests':data}})

    def add_to_set(self, report_id, data):
        self.verify_set_add(data)
        Report.objects(id = report_id).update_one(set__modified = datetime.datetime.now())
        if data["_type"] == "test" and not "scenarioId" in data:
            if data["result"] == False:
                result = self.collection.update_one({ "_id": ObjectId(report_id) }, {'$set': {'message':"Failure", 'result':data["result"]}})
            result = self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"path": data["path"]}} }, {'$push': {'tests.$.tests':data}})
        elif data["_type"] == "scenario" and "scenarioId" in data:
            result = self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"path": data["path"]}} }, {'$push': {'tests.$.tests':data}})
            if data["result"] == False:
                result = self.collection.update_one({ "_id": ObjectId(report_id) }, {'$set': {'message':"Failure", 'result':data["result"]}})
                result = self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"scenarioId": ObjectId(data["scenarioId"])}}}, {'$set': {'tests.$.result':data["result"]}, '$set': {'tests.$.message':"Failure"}})
        elif data["_type"] == "test" and data["scenarioId"]:
            if data["result"] == False:
                result = self.collection.update_one({ "_id": ObjectId(report_id) }, {'$set': {'message':"Failure", 'result':data["result"]}})
                result = self.collection.update_one({ "_id": ObjectId(report_id) }, {'$set': {'tests.$[a].tests.$[b].message':data["message"], 'tests.$[a].tests.$[b].result':data["result"]}}, array_filters=[{"a.path":data["path"]}, {"b.scenarioId":data["scenarioId"]}])
                result = self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"path": data["path"]}}}, {'$set': {'tests.$.result':data["result"], 'tests.$.message':"Failure"}})
            result = self.collection.update_one({ "_id": ObjectId(report_id) }, {'$push': {'tests.$[a].tests.$[b].tests':data}}, array_filters=[{"a.path":data["path"]}, {"b.scenarioId":data["scenarioId"]}])


    def verify_set_add(self, data):
        if not "path" in data or not data["path"]:
            raise ValidationError(errors = {"path": "Please provide a valid path to add append a report"})

    def finish(self, report_id, path, result = True, message = "Success"):
        report = json.loads(Report.objects(id=report_id).get().to_json())
        if report["kind"] == "feature":
            result, message = self.finish_feature_report(report, result, message)
            self.final_finish(report_id, result, message)
            return self.common.create_response(204)
        elif report["kind"] == "set":
            finished = True
            if not path in report["features"]:
                raise ValidationError(errors = {"path":"Path does not exist in the set"})
            for test in report["tests"]:
                if test["path"] == path:
                    result, message = self.finish_feature_report(test, result, message)
                    self.collection.update_one({ "_id": ObjectId(report_id), "tests": {"$elemMatch": {"path": path}}}, {'$set': {'tests.$.result':result, 'tests.$.message':message, 'tests.$.end':datetime.datetime.now()}})
            self.finish_set(report_id)
            return self.common.create_response(204)

    def finish_feature_report(self, report, result = True, message = "Success"):
        for test in report["tests"]:
            if not "result" in test or test["result"] == False:
                result = False
                message = "Failure"
                break
        return result, message

    def final_finish(self, report_id, result, message):
        Report.objects(id = report_id).modify(set__end = datetime.datetime.now(), set__modified = datetime.datetime.now(), set__result = result, set__message = message)

    def finish_set(self, report_id):
        report = json.loads(Report.objects(id=report_id).get().to_json())
        finished = True
        for feature in report["tests"]:
            if not "end" in feature:
                finished = False
                break
        if finished == True:
            result, message = self.finish_feature_report(report)
            Report.objects(id = report_id).update_one(set__end = datetime.datetime.now(), set__modified = datetime.datetime.now(), set__result = result, set__message = message)
