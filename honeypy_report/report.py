import re
from cerberus import Validator
from copy import deepcopy
from flask import Flask, Response, request
from flask_cors import CORS
from honeypy.api.common import Common, Database
from honeypy.errors import ValidationError
from honeypy_report import report_api
from honeypy_report.schema import Schemas
from pymongo.errors import DuplicateKeyError
from honeypy_report.controller import ReportController
"""
    Allow Cross origin requests while in development
"""
CORS(report_api, resources={r'\/report\/?.*': {'origins': 'http://localhost:4200'}})

"""
    Instantiate Database, Common and Validator
"""
common = Common()
validator = Validator({}, purge_unknown = True)

@report_api.route("/report", methods = ["POST"])
def post_report():
    try:
        return ReportController().create(request.get_json())
    except ValidationError as error:
        return Common().create_response(400, error.errors)

@report_api.route("/report/<report_id>", methods = ["GET"])
def get_report(report_id):
    return ReportController().get(report_id)

@report_api.route("/report/<report_id>", methods = ["PATCH"])
def patch_report(report_id):
    try:
        return ReportController().save(report_id, request.get_json())
    except ValidationError as error:
        return Common().create_response(400, error.errors)

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
    report_api.run(host=report_api.config["REPORT_IP"], port=report_api.config["REPORT_PORT"], threaded=True)
