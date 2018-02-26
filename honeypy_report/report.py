from flask import Flask, Response
from flask import request
from flask_cors import CORS, cross_origin

from honeypy_report.controller import ReportController
from honeypy_report import report_api
from honeypy.errors import CustomFileNotFound
from honeypy.api.common import Common
from mongoengine import *
from flask_mongoengine import MongoEngine
from bson.errors import InvalidId

"""
    Configure service
"""
report_api.config['MONGODB_SETTINGS'] = {
    'db': report_api.config["REPORT_DB"],
    'host': report_api.config["DATABASE_IP"],
    'port': report_api.config["DATABASE_PORT"]
}
db = MongoEngine()
db.init_app(report_api)
common = Common()
CORS(report_api, resources={r'\/report\/?.*': {'origins': 'http://localhost:4200'}})

@report_api.route("/report", methods = ["POST"])
def post_report():
    try:
        data = request.get_json()
        return ReportController().create(data)
    except (OperationError, InvalidQueryError, FieldDoesNotExist) as error:
        return common.error(error)
    except CustomFileNotFound as error:
        return common.create_response(404, {"errors":{"path": "File not found"}})

@report_api.route("/report/<report_id>", methods = ["GET"])
def get_report(report_id):
    try:
        return ReportController().get(report_id)
    except (DoesNotExist, ValidationError) as error:
        return common.error(error)

@report_api.route("/report/<report_id>", methods = ["PATCH"])
def patch_report(report_id):
    try:
        data = request.get_json()
        return ReportController().save(report_id, data)
    except (ValidationError, OperationError, InvalidQueryError, FieldDoesNotExist, InvalidId) as error:
        return common.error(error)

@report_api.route("/report/<report_id>/add", methods = ["POST"])
def add_test(report_id):
    try:
        data = request.get_json()
        return ReportController().add(report_id, data)
    except (OperationError, InvalidQueryError, FieldDoesNotExist, InvalidId, ValidationError) as error:
        return common.error(error)

# @report_api.route("/report/search", methods = ["POST"])
# def getReportsByDate():
#     try:
#         data = request.get_json()
#         results = ReportController().getReportsByDate(data)
#         return createResponse(results)
#     except ValidationError as error:
#         return common.validation_error(error)
#
#
@report_api.route("/report/<report_id>/finish", methods = ["GET"])
def finish(report_id):
    path = request.args.get('path')
    return ReportController().finish(report_id, path)
#
# @report_api.route("/report/<reportId>", methods = ["DELETE"])
# def deleteReport(reportId):
#     response = ReportController(reportId).deleteReport()
#     return createResponse(response)


def main():
    if report_api.config["PRODUCTION"]:
        report_api.run(host=report_api.config["IP"], port=report_api.config["PORT"], threaded=True)
    else:
        report_api.run(host=report_api.config["HOST_IP"], port=report_api.config["HOST_PORT"], threaded=True)
