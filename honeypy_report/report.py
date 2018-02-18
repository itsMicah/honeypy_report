"""

    HONEYPY REPORT SERVICE

    Honeypy Report Service maintains reports, organization, and statuses

"""


"""
    Import flask service dependencies
"""
from flask import Flask, request
from flask_cors import CORS

"""
    Import Honeypy libs
"""
from honeypy.api.common import Common
from honeypy.errors import ValidationError

"""
    Honeypy report imports
"""
from honeypy_report import report_api
from honeypy_report.controller import ReportController

"""
    Allow Cross origin requests while in development
"""
CORS(report_api, resources={r'\/report\/?.*': {'origins': 'http://localhost:4200'}})

"""
    Instantiate Common
"""
common = Common()

"""
    Create a report endpoint
"""
@report_api.route("/report", methods = ["POST"])
def post_report():
    try:
        return ReportController().create(request.get_json())
    except ValidationError as error:
        return Common().create_response(400, error.errors)

"""
    Get a report by ID endpoint
"""
@report_api.route("/report/<report_id>", methods = ["GET"])
def get_report(report_id):
    return ReportController().get(report_id)

"""
    Partial update a report by ID
"""
@report_api.route("/report/<report_id>", methods = ["PATCH"])
def patch_report(report_id):
    try:
        return ReportController().save(report_id, request.get_json())
    except ValidationError as error:
        return Common().create_response(400, error.errors)

"""
    Add test objects to a feature report
"""
@report_api.route("/report/<report_id>/add", methods = ["POST"])
def add_test(report_id):
    try:
        return ReportController().add(report_id, request.get_json())
    except ValidationError as error:
        return Common().create_response(400, error.errors)

"""
    Finish a feature report
    Also update a set report result if the feature is part of a set run
"""
@report_api.route("/report/<report_id>/finish", methods = ["GET"])
def finish(report_id):
    try:
        path = request.args.get('path')
        return ReportController().finish(report_id, path)
    except ValidationError as error:
        return Common().create_response()

def main():
    """
        Start the service
    """
    report_api.run(host=report_api.config["REPORT_IP"], port=report_api.config["REPORT_PORT"], threaded=True)
