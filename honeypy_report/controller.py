import time, json, pymongo, re, datetime
from cerberus import Validator
from pymongo import MongoClient
from flask import Flask
from copy import deepcopy
from honeypy.api.test import TestService
from honeypy.api.set import SetService
from honeypy.api.environment import EnvironmentService
from bson.objectid import ObjectId
from bson.errors import InvalidId
from honeypy.errors import CustomFileNotFound, ValidationError

from honeypy_report.schema import Schemas
from honeypy_report import api
from honeypy.common import Common
from honeypy.database import Database

class ReportController(object):

    def __init__(self):
        self.config = api.config
        self.common = Common()
        self.ifFinish = False
        self.environment = {}
        self.db = Database(api.config['DATABASE_IP'], api.config['DATABASE_PORT'], api.config['REPORT_DB_NAME'], api.config['REPORT_DB_COLLECTION'])

    def get(self, report_id):
        """
            Get a report by ID and kind

            :kind: the type of report
            :report_id: the id of the requested report
        """
        report = self.db.find_one({"_id":ObjectId(report_id)})
        if report:
            report = self.get_set_features(report)
            return self.common.create_response(200, report)
        else:
            return self.common.create_response(400, {"reportId": [f"Report ID does not exist ({report_id})"]})

    def get_set_features(self, report):
        """
            Get all feature reports of a set and combine them with set report

            :report: the set report
        """
        if report["kind"] == "set":
            for feature in report["reports"]:
                index = report["reports"].index(feature)
                if "reportId" in feature and feature["reportId"]:
                    feature_report = self.db.find_one({"_id":ObjectId(feature["reportId"])})
                    feature_report["_id"] = str(feature_report["_id"])
                    report["reports"][index] = feature_report
        return report

    def create(self, data):
        """
            Create a report

            :data: the request payload
        """
        data = self.validate_report(data)
        response = None
        data = self.get_environment_variables(data, init = True)
        data = self.check_base_url(data)
        if data["kind"] == "set":
            response = self.create_set_report(data)
        elif data["kind"] == "feature":
            response = self.create_feature_report(data)
        return self.common.create_response(201, {"id":str(response.inserted_id)})

    def create_feature_report(self, data):
        if "parentId" in data:
            self.check_inheritance(data["parentId"], data)
        return self.db.insert_one(data)

    def create_set_report(self, data):
        """
            Create a set report

            :data: the request payload
        """
        response = self.db.insert_one(data)
        for path in data["features"]:
            parentId = response.inserted_id
            self.create_set_feature(path, parentId, data)
        return response

    def get_environment_variables(self, data, init = False):
        if data["environment"]:
            if init:
                response = EnvironmentService().get(data["environment"])
                if response.status_code == 200:
                    self.environment = response.json()
                    self.variables = self.environment["variables"]
            data["environment"] = self.environment
        return data

    def create_set_feature(self, path, parentId, _set):
        """
            Create a set feature report
            Check to see if feature exists before creating a report

            :path: path to the feature
            :parentId: the set report ID
        """
        feature = {"path":path}
        response = TestService().get(path, "feature")
        if response.status_code == 200:
            data = response.json()
            data["parentId"] = str(parentId)
            response = self.create(data)
            feature["reportId"] = json.loads(response.response[0])["id"]
            feature["message"] = "Success"
            self.db.update_one({"_id":ObjectId(parentId)}, {"$push":{"reports": feature}})
        else:
            feature = {"kind":"feature", "path":path, "result":None, "message":None, "status":None}
            self.db.update_one({"_id":ObjectId(parentId)}, {"$push":{"reports": feature}})

    def check_inheritance(self, setId, feature):
        """
            Check whether to make features of set inherit from set
        """
        response = self.get(setId)
        setReport = json.loads(response.response[0])
        if setReport["inherit"] == True:
            feature["browser"] = setReport["browser"]
            feature["url"] = setReport["url"]
            feature["host"] = setReport["host"]
            feature["environment"] = setReport["environment"]
        return feature

    def check_base_url(self, data):
        """
            Check if environment contains an overwriting base url
            If so, change the report base url
        """
        if data["environment"]:
            if "base_url" in data["environment"]["variables"]:
                data["url"] = data["environment"]["variables"]["base_url"]
        return data

    def validate_report(self, data, update = False, normalize = True):
        """
            Validate a feature/set report

            :data: the request payload
            :update: should service validate report as an update action
            :normalize: should default values be defined
        """
        validator = Validator(Schemas().report, allow_unknown = True, ignore_none_values = True)
        data = self.normalize(normalize, data, validator)
        validation = validator.validate(data, update = update)
        if not validation:
            raise ValidationError(validator.errors)
        return self.validate_report_type(data, update, normalize)

    def validate_report_type(self, data, update, normalize):
        """
            Validate report type

            :data: the report
            :update: should service validate report as an update action
            :normalize: should default values be defined
        """
        validator = Validator(Schemas().kind, allow_unknown = True)
        data = self.normalize(normalize, data, validator)
        validation = validator.validate(data)
        if not validation:
            raise ValidationError(validator.errors)
        if data["kind"] == "set":
            data = self.validate_set_report(data, update, normalize)
        elif data["kind"] == "feature":
            data = self.validate_feature_report(data, update, normalize)
        return data

    def validate_set_report(self, data, update, normalize):
        """
            Validate a set report

            :data: the set data
            :update: should service validate report as an update action
            :normalize: should default values be defined
        """
        validator = Validator(Schemas().set_report, purge_unknown = True)
        data = self.normalize(normalize, data, validator)
        validation = validator.validate(data, update = update)
        if not validation:
            raise ValidationError(validator.errors)
        return data

    def validate_feature_report(self, data, update, normalize):
        """
            Validate a feature report

            :data: the feature data
            :update: should service validate report as an update action
            :normalize: should default values be defined
        """
        validator = Validator(Schemas().feature_report, purge_unknown = True)
        data = self.normalize(normalize, data, validator)
        validation = validator.validate(data, update = update)
        if not validation:
            raise ValidationError(validator.errors)
        return data

    def normalize(self, normalize, data, validator):
        """
            Check if we need to define default values

            :normalize: should default values be defined
            :data: the request data
            :validation: the Cerberus validator instance
        """
        if normalize:
            data = validator.normalized(data)
        return data

    def save(self, report_id, data):
        """
            Save to a report

            :report_id: the report id
            :data: the data being saved to the report
        """
        data = self.validate_report(data, True, False)
        self.db.update_one({"_id":ObjectId(report_id)}, {"$set": data})
        return self.common.create_response(204)

    def add(self, report_id, data):
        """
            Check to see where the data will be sent

            :report_id: the report id
            :data: the data being add to the report
        """
        data = self.validate_add(report_id, data)
        if data["type"] == "step":
            self.add_test(report_id, data)
        elif data["type"] == "scenario":
            self.add_scenario(report_id, data)
        self.update_report_result(report_id, data)
        return self.common.create_response(204)

    def validate_add(self, report_id, data):
        """
            Validate add type

            :report_id: the report id we are modifying
            :data: the data we want to add to the report
        """
        validator = Validator(Schemas().add, allow_unknown = True)
        validation = validator.validate(data)
        if not validation:
            raise ValidationError(validator.errors)
        if data["type"] == "test":
            data = self.validate_step_add(report_id, data)
        elif data["type"] == "scenario":
            data = self.validate_scenario_add(report_id, data)
        return data

    def validate_step_add(self, report_id, step):
        """
            Validate a step object

            :report_id: the report id
            :step: the step data
        """
        validator = Validator(Schemas().step, purge_unknown = True)
        step = validator.normalized(step)
        validation = validator.validate(step)
        if not validation:
            raise ValidationError(validator.errors)
        return step

    def validate_scenario_add(self, report_id, scenario):
        """
            Validate a scenario object

            :report_id: the report id
            :scenario: the scenario data
        """
        validator = Validator(Schemas().scenario, purge_unknown = True)
        scenario = validator.normalized(scenario)
        validation = validator.validate(scenario)
        if not validation:
            raise ValidationError(validator.errors)
        return scenario

    def add_scenario(self, report_id, scenario):
        """
            Add a scenario

            :report_id: the report id
            :scenario: the scenario object
        """
        scenario["created"] = self.common.get_timestamp()
        self.db.update_one({"_id":ObjectId(report_id)}, {"$push": {"tests": scenario}})

    def add_test(self, report_id, test):
        """
            Add a test to a report

            :report_id: the report id
            :scenario: the test object
        """
        test["created"] = self.common.get_timestamp()
        if "scenarioId" not in test or not test["scenarioId"]:
            response = self.db.update_one({"_id":ObjectId(report_id)}, {"$push": {"tests": test}})
        else:
            response = self.db.update_one({ "_id": ObjectId(report_id), "tests.scenarioId": test["scenarioId"]}, {'$push': {'tests.$.tests':test}})

    def update_report_result(self, report_id, data):
        """
            Update a report if it failed

            :report_id: the report id
            :data: the test object
        """
        if data["result"] == False:
            report = self.db.find_one({"_id":ObjectId(report_id)})
            self.update_set_result(report, data)
            self.update_feature_result(report, data)
            self.update_scenario_result(report, data)

    def update_set_result(self, report, data):
        """
            Update a set report if the a feature failed

            :report: the report
            :data: the test object
        """
        if "parentId" in report:
            self.db.update_one({"_id":ObjectId(report["parentId"])}, {"$set": {"result":False, "message":"Failure"}})

    def update_feature_result(self, report, data):
        """
            Update a feature report if a feature failed

            :report: the report
            :data: the test object
        """
        self.db.update_one({"_id":ObjectId(report["_id"])}, {"$set": {"result":False, "message":"Failure"}})

    def update_scenario_result(self, report, data):
        """
            Update a scenario within a feature report if a it failed

            :report: the report
            :data: the test object
        """
        if "scenarioId" in data:
            self.db.update_one({"_id":ObjectId(report["_id"]), "tests.scenarioId": data["scenarioId"]}, {'$set': {'tests.$.result':False, "tests.$.message":"Failure"}})

    def finish(self, report_id, path):
        """
            Finish a report

            :report_id: the report id
            :path: the path of the feature
        """
        report = self.db.find_one({"_id": ObjectId(report_id)})
        if not report:
            return self.common.create_response(400, {"reportId": [f"Report ID does not exist ({report_id})"]})
        self.finish_feature_report(report_id, report, path)
        if "parentId" in report:
            self.finish_set_report(report["parentId"])
        return self.common.create_response(204)

    def finish_feature_report(self, report_id, report, path):
        """
            Finish a feature reports

            :report_id: the report id
            :report: the report
            :path: the path of the feature
        """
        report = self.check_report_result(report)
        current_time = self.common.get_timestamp()
        duration = self.get_duration(current_time, report)
        self.db.update_one({"_id": ObjectId(report_id)}, {"$set": {"end": current_time, "result":report["result"], "message":report["message"], "status":"Done", "duration":duration}})
        if "parentId" in report:
            self.db.update_one({"_id": ObjectId(report["parentId"]), "reports.reportId":report["_id"]}, {"$set": {"reports.$.message": report["message"], "reports.$.result":report["result"], "reports.$.status":"Done", "reports.$.fail":report["fail"]}})

    def check_report_result(self, report):
        """
            Check the final report result (pass/fail)

            :report: the report object
        """
        message = ""
        result = None
        if report["result"] == True or report["result"] == None:
            message = "Success"
            result = True
        elif report["result"] == False or report["status"] == "Queued":
            message = "Failure"
            result = False
        report["message"] = message
        report["result"] = result
        return report

    def finish_set_report(self, report_id):
        """
            Finish a set report

            :report_id: the report id
        """
        set_report = self.db.find_one({"_id": ObjectId(report_id)})
        finished = True
        result = True
        message = "Success"
        for feature in set_report["reports"]:
            if "reportId" in feature:
                feature_report = self.db.find_one({"_id": ObjectId(feature["reportId"])})
                feature_report = self.check_report_result(feature_report)
                if not "end" in feature_report:
                    finished = False
                    break
                if feature_report["result"] == False:
                    result = feature_report["result"]
                    message = feature_report["message"]
        if finished == True:
            current_time = self.common.get_timestamp()
            duration = self.get_duration(current_time, set_report)
            self.db.update_one({"_id": ObjectId(report_id)}, {"$set": {"end": current_time, "message":message, "result":result, "status":"Done", "duration":duration}})

    def get_duration(self, current_time, report):
        """
            Calculate the test duration

            :current_time: the current time in milliseconds
            :report: the report used to compare against the current time
        """
        ms = int(current_time) - int(report["created"])
        return time.strftime('%M:%S', time.gmtime(ms/1000))

    def get_dashboard(self, query):
        """
            Get the full dashboard
        """
        query = self.validate_dashboard_query(query)
        browsers = query["browsers"]
        query.pop("browsers")
        dashboard = {}
        query["created"]["$gte"] = query["created"].pop("min")
        query["created"]["$lte"] = query["created"].pop("max")
        for browser in browsers:
            query["browser"] = browser
            reports = self.db.aggregate(query)
            dashboard[browser] = reports
        return self.common.create_response(200, dashboard)

    def validate_dashboard_query(self, query):
        """
            Validate the dashboard search query

            :query: the search query to get the dashboard data
        """
        validator = Validator(Schemas().dashboard, purge_unknown = True)
        query = validator.normalized(query)
        validation = validator.validate(query)
        if not validation:
            raise ValidationError(validator.errors)
        return query

    def search(self, query, deep):
        """
            Search reports

            :query: the search query object
            :deep: specifies if this query is a deep search query
        """
        reports = None
        total = None
        search_total = None
        query = self.validate_search(query)
        query["search"]["created"]["$gte"] = query["search"]["created"].pop("min")
        query["search"]["created"]["$lte"] = query["search"]["created"].pop("max")
        fields = self.return_specific_fields(deep)
        query, skip, page_number = self.get_pagination(query)
        reports, total, search_total = self.db.search(query["search"], skip, query["pagination"]["limit"], query["pagination"]["sort"])
        reports = self.check_search_results(query["search"]["kind"], reports, fields)
        return self.common.create_response(200, {"results": reports, "pagination": {"page":query["pagination"]["page"], "limit":query["pagination"]["limit"], "total": total, "amount":search_total}})

    def set_query_date(self, query):
        """
            Rename date query keys
        """
        query["search"]["created"]["$gte"] = query["search"]["created"].pop("min")
        query["search"]["created"]["$lte"] = query["search"]["created"].pop("max")
        return query

    def get_pagination(self, query):
        """
            Get pagination details
            Return the skip value
            Return the page number value
        """
        page_number = query["pagination"]["page"] - 1
        skip = query["pagination"]["page"] * page_number
        query["pagination"].pop("pagination", None)
        return query, skip, page_number

    def check_search_results(self, kind, reports, fields):
        """
            Check if search was for sets
            If so, get feature reports within sets

            :kind: search kind
            :reports: the return of the search query
        """
        if kind == "set":
            for report in reports:
                result_index = reports.index(report)
                for feature in report["reports"]:
                    set_index = report["reports"].index(feature)
                    _id = None
                    if "reportId" in feature:
                        _id = feature["reportId"]
                    elif "_id" in feature:
                        _id = feature["_id"]
                    feature_report = self.db.find_one({"_id": ObjectId(_id)}, fields)
                    report["reports"][set_index] = feature_report
                reports[result_index] = report
        return reports

    def return_specific_fields(self, deep):
        """
            Specify what fields to return from database query
        """
        if not deep:
            return {"path":1, "name":1, "message":1, "result": 1, "status": 1, "fail":1, 'kind':1, 'parentId':1}

    def validate_search(self, query):
        """
            Validate the search query payload

            :query: the search query object
        """
        validator = Validator(Schemas().search, purge_unknown = True)
        query = validator.normalized(query)
        validation = validator.validate(query)
        if not validation:
            raise ValidationError(validator.errors)
        return query
